"""Generate Obsidian-compatible German vocabulary notes.

The generator:
- translates German vocabulary into English using MyMemory first,
- falls back to Google Translate for English,
- translates German vocabulary and example sentences into Persian
  using MyMemory first,
- falls back to Google Translate for Persian,
- retrieves German pronunciation audio,
- retrieves Persian definitions,
- caches successful translations in memory,
- retries transient translation failures with exponential backoff,
- limits translation request frequency,
- processes independent work concurrently,
- preserves Markdown headers and example formatting.

PONS is intentionally not used here because the current
deep-translator PonsTranslator adapter is incompatible with the
current PONS website structure.
"""

from __future__ import annotations

import asyncio
import time

import aiofiles
from deep_translator import (
    GoogleTranslator,
    MyMemoryTranslator,
)
from deep_translator.exceptions import TranslationNotFound

from learning_german.config.settings import (
    APPEND_MODE,
    ENCODING,
    INPUT_FILE,
    MIN_WORD_LENGTH,
    OUTPUT_FILE,
    READ_MODE,
)
from learning_german.utils.de_pronunciation_retriever import (
    download_audio_async,
    get_audio_url_async,
)
from learning_german.utils.fa_definition_retriever import (
    definition_grabber_async,
)
from learning_german.utils.text_processing import remove_article

TRANSLATION_RETRIES = 3
TRANSLATION_MIN_INTERVAL = 1.2
TRANSLATION_BACKOFF_BASE = 4.0
RESOURCE_CONCURRENCY = 4

translator_mymemory_en = MyMemoryTranslator(
    source="german",
    target="english",
)
translator_google_en = GoogleTranslator(
    source="de",
    target="en",
)
translator_mymemory_fa = MyMemoryTranslator(
    source="german",
    target="persian",
)
translator_google_fa = GoogleTranslator(
    source="de",
    target="fa",
)

_translation_rate_lock = asyncio.Lock()
_last_translation_request = 0.0
resource_semaphore = asyncio.Semaphore(RESOURCE_CONCURRENCY)

translation_cache: dict[str, dict[str, str]] = {
    "en": {},
    "fa": {},
    "def": {},
}

_translation_locks: dict[
    tuple[str, str],
    asyncio.Lock,
] = {}


def get_translation_lock(language: str, text: str) -> asyncio.Lock:
    key = (language, text)
    lock = _translation_locks.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _translation_locks[key] = lock
    return lock


async def wait_for_translation_slot() -> None:
    global _last_translation_request

    async with _translation_rate_lock:
        now = time.monotonic()
        wait_time = TRANSLATION_MIN_INTERVAL - (now - _last_translation_request)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        _last_translation_request = time.monotonic()


async def call_translator(
    translator: MyMemoryTranslator | GoogleTranslator,
    text: str,
) -> str | None:
    await wait_for_translation_slot()

    def translate() -> str:
        return translator.translate(text)

    result = await asyncio.to_thread(translate)

    if result is None:
        return None

    result = str(result).strip()
    return result or None


async def translate_with_retry(
    translator: MyMemoryTranslator | GoogleTranslator,
    text: str,
    language: str,
) -> str | None:
    for attempt in range(TRANSLATION_RETRIES):
        try:
            result = await call_translator(translator, text)

            if result:
                return result

            raise TranslationNotFound(text)

        except TranslationNotFound as exc:
            if attempt == TRANSLATION_RETRIES - 1:
                print(
                    f"Provider failed after "
                    f"{TRANSLATION_RETRIES} attempts "
                    f"for '{text}' ({language}): {exc}"
                )
                return None

            backoff = TRANSLATION_BACKOFF_BASE**attempt

            print(
                f"Translation attempt "
                f"{attempt + 1}/{TRANSLATION_RETRIES} failed "
                f"for '{text}' ({language}). "
                f"Retrying in {backoff:.1f}s..."
            )

            await asyncio.sleep(backoff)

        except Exception as exc:
            if attempt == TRANSLATION_RETRIES - 1:
                print(
                    f"Provider failed after "
                    f"{TRANSLATION_RETRIES} attempts "
                    f"for '{text}' ({language}): {exc}"
                )
                return None

            backoff = TRANSLATION_BACKOFF_BASE**attempt

            print(
                f"Translation attempt "
                f"{attempt + 1}/{TRANSLATION_RETRIES} failed "
                f"for '{text}' ({language}): {exc}. "
                f"Retrying in {backoff:.1f}s..."
            )

            await asyncio.sleep(backoff)

    return None


async def get_english_translation(text: str) -> str | None:
    cache = translation_cache["en"]

    if text in cache:
        return cache[text]

    lock = get_translation_lock("en", text)

    async with lock:
        if text in cache:
            return cache[text]

        result = await translate_with_retry(
            translator_mymemory_en,
            text,
            "en",
        )

        if result is not None:
            cache[text] = result
            return result

        print(f"MyMemory failed for '{text}'. Trying Google Translate...")

        result = await translate_with_retry(
            translator_google_en,
            text,
            "en",
        )

        if result is not None:
            cache[text] = result
            return result

        print(f"All English translation providers failed for '{text}'.")

        return None


async def get_persian_translation(text: str) -> str | None:
    cache = translation_cache["fa"]

    if text in cache:
        return cache[text]

    lock = get_translation_lock("fa", text)

    async with lock:
        if text in cache:
            return cache[text]

        result = await translate_with_retry(
            translator_mymemory_fa,
            text,
            "fa",
        )

        if result is not None:
            cache[text] = result
            return result

        print(f"MyMemory failed for '{text}' (fa). Trying Google Translate...")

        result = await translate_with_retry(
            translator_google_fa,
            text,
            "fa",
        )

        if result is not None:
            cache[text] = result
            return result

        print(f"All Persian translation providers failed for '{text}'.")

        return None


async def get_audio(word: str) -> str | None:
    base_word = remove_article(word)
    search_word = base_word.lower().replace(" ", "")

    try:
        async with resource_semaphore:
            audio_url = await get_audio_url_async(search_word)

        if not isinstance(audio_url, str) or not audio_url:
            return None

        async with resource_semaphore:
            await download_audio_async(audio_url, base_word)

        return audio_url

    except asyncio.CancelledError:
        raise

    except Exception as exc:
        print(f"Audio error for '{word}': {exc}")
        return None


async def get_definition(base_word: str) -> str:
    cache = translation_cache["def"]

    if base_word in cache:
        return cache[base_word]

    try:
        async with resource_semaphore:
            definition = await definition_grabber_async(base_word)

        if definition:
            cache[base_word] = definition

        return definition or ""

    except asyncio.CancelledError:
        raise

    except Exception as exc:
        print(f"Definition error for '{base_word}': {exc}")
        return ""


async def process_word_async(word: str) -> str:
    word = word.strip().replace("\ufeff", "")
    base_word = remove_article(word)

    audio_task = asyncio.create_task(get_audio(word))
    definition_task = asyncio.create_task(get_definition(base_word))
    en_task = asyncio.create_task(get_english_translation(word))
    fa_task = asyncio.create_task(get_persian_translation(word))

    try:
        (
            audio_url,
            definition,
            en_translation,
            fa_translation,
        ) = await asyncio.gather(
            audio_task,
            definition_task,
            en_task,
            fa_task,
        )

    except asyncio.CancelledError:
        for task in (
            audio_task,
            definition_task,
            en_task,
            fa_task,
        ):
            task.cancel()

        await asyncio.gather(
            audio_task,
            definition_task,
            en_task,
            fa_task,
            return_exceptions=True,
        )

        raise

    en_translation = (
        en_translation if en_translation is not None else f"[Translation failed: {word}]"
    )

    fa_translation = (
        fa_translation if fa_translation is not None else f"[Translation failed: {word}]"
    )

    output = f"> [!tldr]- {word}\n"

    if audio_url:
        output += f"> ![[{base_word}.wav]]\n"

    output += f"> {en_translation}\n"
    output += f"> {fa_translation}\n"
    output += f"{definition}\n"

    if audio_url:
        print(f"Processed: '{word}'")
    else:
        print(f"Processed: '{word}', No audio file was found!")

    return output


async def process_example_sentence(word: str) -> str:
    original = word.strip().replace("\ufeff", "")
    sentence = original.removeprefix("> ").strip()

    translation = await get_persian_translation(sentence)

    if translation is None:
        translation = "[Translation failed]"

    return f"> [!warning]- 📝 Beispiel Satz:\n{original}\n> {translation}\n\n"


def is_header(line: str) -> bool:
    return line.startswith(("#", "\ufeff#", "---"))


def is_example_sentence(line: str) -> bool:
    return line.startswith(("> ", "\ufeff> "))


def is_processable_word(line: str) -> bool:
    return len(line.strip()) > MIN_WORD_LENGTH


async def process_lines_async(words: list[str]) -> None:
    async with aiofiles.open(
        OUTPUT_FILE,
        APPEND_MODE,
        encoding=ENCODING,
    ) as output_file:
        for line in words:
            word = line.replace("\ufeff", "").rstrip("\n")

            if is_header(word):
                await output_file.write(f"{word}\n")

                print(f"Processed: '{word.strip()}', as a header.")

            elif is_example_sentence(word):
                result = await process_example_sentence(word)
                await output_file.write(result)

                print(f"Processed: '{word.strip()}', as an example sentence.")

            elif is_processable_word(word):
                result = await process_word_async(word)
                await output_file.write(result)


def print_statistics(elapsed_time: float) -> None:
    print(f"\nProcessing completed in {elapsed_time:.2f} seconds")

    print(
        "Cache statistics: "
        f"English translations: "
        f"{len(translation_cache['en'])}, "
        f"Persian translations: "
        f"{len(translation_cache['fa'])}, "
        f"Definitions: "
        f"{len(translation_cache['def'])}"
    )


async def main_async() -> None:
    start_time = time.perf_counter()

    try:
        async with aiofiles.open(
            INPUT_FILE,
            READ_MODE,
            encoding=ENCODING,
        ) as basefile:
            words = await basefile.readlines()

        await process_lines_async(words)

    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found!")

    except PermissionError:
        print(f"Error: Permission denied accessing '{INPUT_FILE}' or '{OUTPUT_FILE}'")

    except asyncio.CancelledError:
        print("\nProcessing cancelled.")
        raise

    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")

    else:
        elapsed_time = time.perf_counter() - start_time
        print_statistics(elapsed_time)


def main_async_wrapper() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")


def main() -> None:
    main_async_wrapper()


if __name__ == "__main__":
    main()

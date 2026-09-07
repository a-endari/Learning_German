"""Generate Obsidian-compatible German vocabulary notes.

The generator:
- translates German vocabulary into English and Persian,
- translates example sentences into Persian,
- retrieves German pronunciation audio,
- retrieves Persian definitions,
- caches successful translations in memory,
- retries transient translation failures with exponential backoff,
- limits translation request frequency,
- processes independent work concurrently,
- preserves Markdown headers and example formatting.

The implementation intentionally uses only the project's existing dependencies.
"""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

import aiofiles
from deep_translator import GoogleTranslator
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


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TRANSLATION_RETRIES = 6

# Minimum/maximum delay between successful translation requests.
TRANSLATION_MIN_DELAY = 1.1
TRANSLATION_MAX_DELAY = 2.1

# Base used for exponential backoff after a failed request.
TRANSLATION_BACKOFF_BASE = 2.0

# Prevent too many translation requests from running simultaneously.
TRANSLATION_CONCURRENCY = 2

# Maximum number of audio/definition operations running simultaneously.
RESOURCE_CONCURRENCY = 4


# ---------------------------------------------------------------------------
# Shared services
# ---------------------------------------------------------------------------

translator_en = GoogleTranslator(source="de", target="en")
translator_fa = GoogleTranslator(source="de", target="fa")

translation_semaphore = asyncio.Semaphore(TRANSLATION_CONCURRENCY)
resource_semaphore = asyncio.Semaphore(RESOURCE_CONCURRENCY)


# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

translation_cache: dict[str, dict[str, str]] = {
    "en": {},
    "fa": {},
    "def": {},
}


# Prevent multiple concurrent requests for the exact same item.
_translation_locks: dict[tuple[str, str], asyncio.Lock] = {}


T = TypeVar("T")


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def get_translation_lock(language: str, text: str) -> asyncio.Lock:
    """Return the lock associated with one translation request."""

    key = (language, text)

    lock = _translation_locks.get(key)

    if lock is None:
        lock = asyncio.Lock()
        _translation_locks[key] = lock

    return lock


async def run_limited(
    semaphore: asyncio.Semaphore,
    operation: Callable[[], Awaitable[T]],
) -> T:
    """Run an async operation while respecting a concurrency limit."""

    async with semaphore:
        return await operation()


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------


async def translate_with_retry(
    translator: GoogleTranslator,
    text: str,
    language: str,
) -> str | None:
    """Translate text with retries and exponential backoff.

    Returns:
        The translated text on success.
        None if all attempts fail.
    """

    for attempt in range(TRANSLATION_RETRIES):
        try:
            async with translation_semaphore:
                result = await asyncio.to_thread(
                    translator.translate,
                    text,
                )

                # Google Translate is being accessed through an unofficial
                # web-scraping wrapper, so deliberately avoid hammering it.
                delay = random.uniform(
                    TRANSLATION_MIN_DELAY,
                    TRANSLATION_MAX_DELAY,
                )

            await asyncio.sleep(delay)

            if result and result.strip():
                return result.strip()

            raise TranslationNotFound(text)

        except TranslationNotFound as exc:
            if attempt == TRANSLATION_RETRIES - 1:
                print(
                    f"Translation failed after "
                    f"{TRANSLATION_RETRIES} attempts "
                    f"for '{text}' ({language}): {exc}"
                )
                return None

            backoff = TRANSLATION_BACKOFF_BASE**attempt + random.uniform(0.5, 1.5)

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
                    f"Translation failed after "
                    f"{TRANSLATION_RETRIES} attempts "
                    f"for '{text}' ({language}): {exc}"
                )
                return None

            backoff = TRANSLATION_BACKOFF_BASE**attempt + random.uniform(0.5, 1.5)

            print(
                f"Translation attempt "
                f"{attempt + 1}/{TRANSLATION_RETRIES} failed "
                f"for '{text}' ({language}): {exc}. "
                f"Retrying in {backoff:.1f}s..."
            )

            await asyncio.sleep(backoff)

    return None


async def get_translation(
    text: str,
    language: str,
) -> str | None:
    """Return a cached translation or fetch one safely."""

    cache = translation_cache[language]

    if text in cache:
        return cache[text]

    lock = get_translation_lock(language, text)

    async with lock:
        # Another task may have completed the translation while this
        # coroutine was waiting for the lock.
        if text in cache:
            return cache[text]

        translator = translator_en if language == "en" else translator_fa

        result = await translate_with_retry(
            translator,
            text,
            language,
        )

        # Cache only successful translations.
        #
        # Failed results must NOT be cached, otherwise one temporary
        # Google failure permanently poisons the current process.
        if result is not None:
            cache[text] = result

        return result


# ---------------------------------------------------------------------------
# Audio / definition helpers
# ---------------------------------------------------------------------------


async def get_audio(word: str) -> str | None:
    """Retrieve and download pronunciation audio for a word."""

    base_word = remove_article(word)
    search_word = base_word.lower().replace(" ", "")

    try:
        async with resource_semaphore:
            audio_url = await get_audio_url_async(search_word)

        if not audio_url:
            return None

        async with resource_semaphore:
            await download_audio_async(
                audio_url,
                base_word,
            )

        return audio_url

    except asyncio.CancelledError:
        raise

    except Exception as exc:
        print(f"Audio error for '{word}': {exc}")
        return None


async def get_definition(base_word: str) -> str:
    """Retrieve the Persian definition for a word."""

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


# ---------------------------------------------------------------------------
# Vocabulary processing
# ---------------------------------------------------------------------------


async def process_word_async(word: str) -> str:
    """Process one vocabulary item."""

    word = word.strip().replace("\ufeff", "")

    base_word = remove_article(word)

    # These operations are independent, so start them together.
    audio_task = asyncio.create_task(get_audio(word))

    definition_task = asyncio.create_task(get_definition(base_word))

    en_task = asyncio.create_task(get_translation(word, "en"))

    fa_task = asyncio.create_task(get_translation(word, "fa"))

    try:
        audio_url, definition, en_translation, fa_translation = await asyncio.gather(
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
        output += f"> ![[{base_word}.wav]]\n> {en_translation}\n> {fa_translation}\n{definition}\n"

        print(f"Processed: '{word}'")

    else:
        output += f"> {en_translation}\n> {fa_translation}\n{definition}\n"

        print(f"Processed: '{word}', No audio file was found!")

    return output


# ---------------------------------------------------------------------------
# Example sentence processing
# ---------------------------------------------------------------------------


async def process_example_sentence(word: str) -> str:
    """Translate and format a German example sentence."""

    original = word.strip().replace("\ufeff", "")

    # Remove Markdown blockquote syntax before sending text to Google.
    sentence = original.removeprefix("> ").strip()

    translation = await get_translation(
        sentence,
        "fa",
    )

    if translation is None:
        translation = "[Translation failed]"

    return f"> [!warning]- 📝 Beispiel Satz:\n{original}\n> {translation}\n\n"


# ---------------------------------------------------------------------------
# Input classification
# ---------------------------------------------------------------------------


def is_header(line: str) -> bool:
    """Return whether a line is a Markdown/header separator."""

    return line.startswith(
        (
            "#",
            "\ufeff#",
            "---",
        )
    )


def is_example_sentence(line: str) -> bool:
    """Return whether a line is a Markdown blockquote."""

    return line.startswith(
        (
            "> ",
            "\ufeff> ",
        )
    )


def is_processable_word(line: str) -> bool:
    """Return whether a line should be processed as vocabulary."""

    return len(line.strip()) > MIN_WORD_LENGTH


# ---------------------------------------------------------------------------
# Line processing
# ---------------------------------------------------------------------------


async def process_lines_async(
    words: list[str],
) -> None:
    """Process input lines and append generated Markdown to the output."""

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def print_statistics(elapsed_time: float) -> None:
    """Print processing statistics."""

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
    """Run the Markdown note generator."""

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
    """Synchronous wrapper for the asynchronous application."""

    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")


def main() -> None:
    """CLI entry point."""

    main_async_wrapper()


if __name__ == "__main__":
    main()

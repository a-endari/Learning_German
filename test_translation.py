"""Markdown Note Generator.

Translates German words to English and Persian, downloads audio,
and formats the results as Markdown.
"""

import asyncio
import random
import time
from typing import Dict

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

TRANSLATION_RETRIES = 4
TRANSLATION_MIN_DELAY = 1.0
TRANSLATION_MAX_DELAY = 2.0
TRANSLATION_BACKOFF_BASE = 2.0


# ---------------------------------------------------------------------------
# Translators
# ---------------------------------------------------------------------------

translator_en = GoogleTranslator(source="de", target="en")
translator_fa = GoogleTranslator(source="de", target="fa")


# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

translation_cache: Dict[str, Dict[str, str]] = {
    "en": {},
    "fa": {},
    "def": {},
}


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------


async def translate_with_retry(
    translator: GoogleTranslator,
    text: str,
    language: str,
) -> str | None:
    """Translate text with retries and exponential backoff.

    Failed translations are not cached so they can be retried later.

    Args:
        translator: Configured deep-translator translator.
        text: German text to translate.
        language: Target language name used for logging.

    Returns:
        The translated text, or None if all attempts fail.
    """
    for attempt in range(TRANSLATION_RETRIES):
        try:
            result = await asyncio.to_thread(
                translator.translate,
                text,
            )

            # Add a small delay after successful requests to avoid
            # hammering Google's unofficial translation endpoint.
            delay = random.uniform(
                TRANSLATION_MIN_DELAY,
                TRANSLATION_MAX_DELAY,
            )
            await asyncio.sleep(delay)

            return result

        except TranslationNotFound as exc:
            if attempt == TRANSLATION_RETRIES - 1:
                print(
                    f"Translation failed after {TRANSLATION_RETRIES} attempts "
                    f"for '{text}' ({language}): {exc}"
                )
                return None

            delay = TRANSLATION_BACKOFF_BASE**attempt + random.uniform(0.5, 1.5)

            print(
                f"Translation attempt {attempt + 1}/{TRANSLATION_RETRIES} "
                f"failed for '{text}' ({language}). "
                f"Retrying in {delay:.1f}s..."
            )

            await asyncio.sleep(delay)

        except Exception as exc:
            if attempt == TRANSLATION_RETRIES - 1:
                print(
                    f"Unexpected translation error after "
                    f"{TRANSLATION_RETRIES} attempts for "
                    f"'{text}' ({language}): {exc}"
                )
                return None

            delay = TRANSLATION_BACKOFF_BASE**attempt + random.uniform(0.5, 1.5)

            print(
                f"Translation error on attempt "
                f"{attempt + 1}/{TRANSLATION_RETRIES} "
                f"for '{text}' ({language}): {exc}. "
                f"Retrying in {delay:.1f}s..."
            )

            await asyncio.sleep(delay)

    return None


async def get_translation(
    word: str,
    language: str,
) -> str | None:
    """Get a cached translation or request a new one.

    Args:
        word: German word or sentence.
        language: Target language ('en' or 'fa').

    Returns:
        Translation string, or None if translation failed.
    """
    if word in translation_cache[language]:
        return translation_cache[language][word]

    if language == "en":
        translator = translator_en
    elif language == "fa":
        translator = translator_fa
    else:
        raise ValueError(f"Unsupported translation language: {language}")

    translation = await translate_with_retry(
        translator,
        word,
        language.upper(),
    )

    # Only cache successful translations.
    if translation is not None:
        translation_cache[language][word] = translation

    return translation


# ---------------------------------------------------------------------------
# Word processing
# ---------------------------------------------------------------------------


async def process_word_async(word: str) -> str:
    """Process a German word and generate its Markdown representation.

    Args:
        word: German word to process.

    Returns:
        Formatted Markdown text.
    """
    # Clean the word and remove BOM characters.
    word = word.strip().replace("\ufeff", "")

    # Get the base word without its article.
    base_word = remove_article(word)

    # Audio search uses the base word without spaces.
    search_word = base_word.lower().replace(" ", "")

    # -----------------------------------------------------------------------
    # Audio
    # -----------------------------------------------------------------------

    audio_url = await get_audio_url_async(search_word)

    if audio_url:
        await download_audio_async(audio_url, base_word)

    # -----------------------------------------------------------------------
    # English translation
    # -----------------------------------------------------------------------

    en_translation = await get_translation(word, "en")

    if en_translation is None:
        en_translation = f"[Translation failed: {word}]"

    # -----------------------------------------------------------------------
    # Persian translation
    # -----------------------------------------------------------------------

    fa_translation = await get_translation(word, "fa")

    if fa_translation is None:
        fa_translation = f"[Translation failed: {word}]"

    # -----------------------------------------------------------------------
    # Persian definition
    # -----------------------------------------------------------------------

    if base_word not in translation_cache["def"]:
        translation_cache["def"][base_word] = await definition_grabber_async(base_word)

    persian_def = translation_cache["def"][base_word]

    # -----------------------------------------------------------------------
    # Markdown output
    # -----------------------------------------------------------------------

    output = f"> [!tldr]- {word}\n"

    if audio_url:
        output += f"> ![[{base_word}.wav]]\n> {en_translation}\n> {fa_translation}\n{persian_def}\n"

        print(f"Processed: '{word}'")

    else:
        output += f"> {en_translation}\n> {fa_translation}\n{persian_def}\n"

        print(f"Processed: '{word}', No audio file was found!")

    return output


# ---------------------------------------------------------------------------
# Line processing
# ---------------------------------------------------------------------------


async def process_lines_async(words: list[str]) -> None:
    """Process input lines and write Markdown output.

    Args:
        words: Lines read from the input file.
    """
    async with aiofiles.open(
        OUTPUT_FILE,
        APPEND_MODE,
        encoding=ENCODING,
    ) as output_file:
        for word in words:
            # Clean BOM before checking line prefixes.
            clean_word = word.replace("\ufeff", "")

            # ---------------------------------------------------------------
            # Headers
            # ---------------------------------------------------------------

            if clean_word.startswith(("#", "---")):
                await output_file.write(f"{word}\n")

                print(f"Processed: '{word.strip()}', as a header.")

            # ---------------------------------------------------------------
            # Example sentences
            # ---------------------------------------------------------------

            elif clean_word.startswith("> "):
                # Remove Markdown blockquote marker before translation.
                sentence = clean_word.removeprefix("> ").strip()

                fa_translation = await get_translation(
                    sentence,
                    "fa",
                )

                if fa_translation is None:
                    fa_translation = "[Translation failed]"

                await output_file.write(
                    f"> [!warning]- 📝 Beispiel Satz:\n{word}> {fa_translation}\n\n"
                )

                print(f"Processed: '{sentence}', as an example sentence.")

            # ---------------------------------------------------------------
            # Vocabulary words
            # ---------------------------------------------------------------

            elif len(clean_word.strip()) > MIN_WORD_LENGTH:
                result = await process_word_async(clean_word)
                await output_file.write(result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main_async() -> None:
    """Read the input file and generate the Markdown output."""
    start_time = time.monotonic()

    try:
        async with aiofiles.open(
            INPUT_FILE,
            READ_MODE,
            encoding=ENCODING,
        ) as basefile:
            words = await basefile.readlines()

        await process_lines_async(words)

        elapsed = time.monotonic() - start_time

        print(f"\nProcessing completed in {elapsed:.2f} seconds")

        print(
            f"Cache statistics: "
            f"English translations: {len(translation_cache['en'])}, "
            f"Persian translations: {len(translation_cache['fa'])}, "
            f"Definitions: {len(translation_cache['def'])}"
        )

    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found!")

    except PermissionError:
        print(f"Error: Permission denied accessing '{INPUT_FILE}' or '{OUTPUT_FILE}'")

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")

    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


def main_async_wrapper() -> None:
    """Wrapper for the async main function."""
    asyncio.run(main_async())


def main() -> None:
    """Synchronous entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

"""Markdown Note Generator: Translates German words to English and Persian, downloads audio, and formats output in markdown."""

import asyncio
import time
from typing import List, Dict

import aiofiles
from deep_translator import GoogleTranslator

from learning_german.config.settings import (
    APPEND_MODE,
    ENCODING,
    INPUT_FILE,
    MIN_WORD_LENGTH,
    OUTPUT_FILE,
    READ_MODE,
)
from learning_german.utils.fa_definition_retriever import (
    definition_grabber,
    definition_grabber_async,
)
from learning_german.utils.de_pronunciation_retriever import (
    download_audio,
    get_audio_url,
    download_audio_async,
    get_audio_url_async,
)
from learning_german.utils.text_processing import remove_article

# Cache for translations and definitions
translation_cache: Dict[str, Dict[str, str]] = {
    'en': {},  # German to English
    'fa': {},  # German to Persian
    'def': {}  # German to Persian definition
}


async def run_in_executor(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


async def process_word_async(word: str) -> str:
    """
    Processes a single German word asynchronously: gets audio, translations, and formats output.

    Args:
        word (str): German word to process
    Returns:
        str: Formatted markdown text with translations and audio
    """
    # Clean the word and remove any BOM characters
    word = word.strip().replace("\ufeff", "")

    # Try to get the base word (without article)
    base_word = remove_article(word)

    # For audio search, try with just the base word (no spaces)
    search_word = base_word.lower().replace(" ", "")

    # Use the async version directly
    audio_url = await get_audio_url_async(search_word)
    if audio_url:
        await download_audio_async(audio_url, base_word)

    # Get translations (with caching)
    if word not in translation_cache['en']:
        translation_cache['en'][word] = await run_in_executor(
            GoogleTranslator(source="de", target="en").translate, word)
    en_translation = translation_cache['en'][word]
    
    if word not in translation_cache['fa']:
        translation_cache['fa'][word] = await run_in_executor(
            GoogleTranslator(source="de", target="fa").translate, word)
    fa_translation = translation_cache['fa'][word]

    # Get Persian definition (with caching)
    if base_word not in translation_cache['def']:
        translation_cache['def'][base_word] = await definition_grabber_async(base_word)
    persian_def = translation_cache['def'][base_word]

    # Format output
    output = f"> [!tldr]- {word}\n"
    if audio_url:
        output += f"> ![[{base_word}.wav]]\n> {en_translation}\n> {fa_translation}\n{persian_def}\n"
        print(f"Processed: '{word.strip()}'")
    else:
        output += f"> {en_translation}\n> {fa_translation}\n{persian_def}\n"
        print(f"Processed: '{word.strip()}', No audio file were found!")
    return output


async def process_lines_async(words: List[str]) -> None:
    """
    Process and write words to output file asynchronously.

    Args:
        words (List[str]): List of words to process
    """
    async with aiofiles.open(
        OUTPUT_FILE, APPEND_MODE, encoding=ENCODING
    ) as output_file:
        # Process words in order
        for word in words:
            if word.startswith(("#", "\ufeff#")):  # Handle headers
                await output_file.write(f"{word}\n")
                print(f"Processed : '{word.strip()}', as a header.")
            elif word.startswith("> ") or word.startswith(
                "\ufeff> "
            ):  # Handle block quotes
                # Cache example sentence translations
                if word not in translation_cache['fa']:
                    translation_cache['fa'][word] = await run_in_executor(
                        GoogleTranslator(source="de", target="fa").translate, word)
                fa_translation = translation_cache['fa'][word]
                
                await output_file.write(
                    f"> [!warning]- 📝 Beispiel Satz:\n{word}{fa_translation}\n\n"
                )
                print(f"Processed : '{word.strip()}', as an example sentence.")
            elif len(word.strip()) > MIN_WORD_LENGTH:  # Process words
                result = await process_word_async(word)
                await output_file.write(result)


async def main_async() -> None:
    """Main async function to process the input file and generate translations."""
    start_time = time.time()

    try:
        async with aiofiles.open(INPUT_FILE, READ_MODE, encoding=ENCODING) as basefile:
            words = await basefile.readlines()

        await process_lines_async(words)

        elapsed_time = time.time() - start_time
        print(f"Processing completed in {elapsed_time:.2f} seconds")
        print(f"Cache statistics: English translations: {len(translation_cache['en'])}, " 
              f"Persian translations: {len(translation_cache['fa'])}, "
              f"Definitions: {len(translation_cache['def'])}")

    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found!")
    except PermissionError:
        print(f"Error: Permission denied accessing '{INPUT_FILE}' or '{OUTPUT_FILE}'")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def main_async_wrapper():
    """Wrapper for the async main function to use as an entry point."""
    asyncio.run(main_async())


# Keep this for backward compatibility
def main():
    """Synchronous wrapper for the async main function."""
    asyncio.run(main_async())


if __name__ == "__main__":
    asyncio.run(main_async())
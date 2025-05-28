"""Markdown Note Generator: Translates German words to English and Persian, downloads audio, and formats output in markdown."""

from typing import List

from deep_translator import GoogleTranslator

from learning_german.config.settings import (
    APPEND_MODE,
    ENCODING,
    INPUT_FILE,
    MIN_WORD_LENGTH,
    OUTPUT_FILE,
    READ_MODE,
)
from learning_german.utils.fa_definition_retriever import definition_grabber
from learning_german.utils.de_pronunciation_retriever import (
    download_audio,
    get_audio_url,
)
from learning_german.utils.text_processing import remove_article


def process_word(word: str) -> str:
    """
    Processes a single German word: gets audio, translations, and formats output.

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

    audio_url = get_audio_url(search_word)

    if audio_url:
        download_audio(audio_url, filename=base_word)

    # Get translations
    translations = {
        "en": GoogleTranslator(source="de", target="en").translate(text=word),
        "fa": GoogleTranslator(source="de", target="fa").translate(text=word),
    }

    # Get Persian definition
    persian_def = definition_grabber(base_word)

    # Format output
    output = f"> [!tldr]- {word}\n"
    if audio_url:
        output += f"> ![[{base_word}.wav]]\n> {translations['en']}\n> {translations['fa']}\n{persian_def}\n"
        print(f"Processed: '{word.strip()}'")
    else:
        output += f"> {translations['en']}\n> {translations['fa']}\n{persian_def}\n"
        print(f"Processed: '{word.strip()}', No audio file were found!")
    return output


def process_lines(words: List[str]) -> None:
    """
    Process and write words to output file.

    Args:
        words (List[str]): List of words to process
    """
    with open(OUTPUT_FILE, APPEND_MODE, encoding=ENCODING) as output_file:
        for word in words:
            if word.startswith(("#", "\ufeff#")):  # Handle headers
                output_file.write(f"{word}\n")
                print(f"Processed : '{word.strip()}', as a header.")
            elif word.startswith("> ") or word.startswith(
                "\ufeff> "
            ):  # Handle block quotes
                output_file.write(
                    f"> [!warning]- 📝 Beispiel Satz:\n{word}{GoogleTranslator(source="de", target="fa").translate(text=word)}\n\n"
                )
                print(f"Processed : '{word.strip()}', as an example sentence.")
            elif len(word.strip()) > MIN_WORD_LENGTH:  # Process words
                result = process_word(word)
                output_file.write(result)


def main() -> None:
    """Main function to process the input file and generate translations."""
    try:
        with open(INPUT_FILE, READ_MODE, encoding=ENCODING) as basefile:
            words = basefile.readlines()

        process_lines(words)

    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found!")
    except PermissionError:
        print(f"Error: Permission denied accessing '{INPUT_FILE}' or '{OUTPUT_FILE}'")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()

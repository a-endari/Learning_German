"""TiM: Translate into Markdown: Translates German words to English and Persian, downloads audio, and formats output in markdown."""

from deep_translator import GoogleTranslator
from audio_grabber_b_amooz import download_audio, get_audio_url
from persian_def import definition_grabber
from typing import List

# Constants
INPUT_FILE = "base.md"
OUTPUT_FILE = "text.md"
READ_MODE = "r"
APPEND_MODE = "a"
ENCODING = "utf-8"
MIN_WORD_LENGTH = 2


def remove_article(word: str) -> str:
    """
    Removes German articles (der, die, das) from the word and returns the base word.

    Args:
        word (str): German word potentially with article
    Returns:
        str: Word without article
    """
    # Dictionary of German articles to remove
    articles = {"der ": "", "die ": "", "der/die ": "", "das ": ""}

    word = word.lower()
    separator = " -"

    # Remove article if present
    for article in articles:
        if word.startswith(article):
            print(word.removeprefix(article).split(separator, 1)[0])  # Log
            return word.removeprefix(article).split(separator, 1)[0]

    # If no article found, return the word with title case
    print(word.lower().split(separator, 1)[0])  # Log
    return word.lower().split(separator, 1)[0]


def process_word(word: str) -> str:
    """
    Processes a single German word: gets audio, translations, and formats output.

    Args:
        word (str): German word to process
    Returns:
        str: Formatted markdown text with translations and audio
    """

    word = word.strip()  # Remove newlines and whitespace
    base_word = remove_article(word)

    # Get audio file URL and download if available
    audio_url = get_audio_url(base_word)
    if audio_url:
        download_audio(audio_url, filename=base_word)
    else:
        print(f"Audio file for {base_word} not found!")

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
        output += f"> ![[{base_word}.wav]]\n"
    output += f"> {translations['en']}\n> {translations['fa']}\n{persian_def}\n"

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
            elif word.startswith("> ") or word.startswith(
                "\ufeff> "
            ):  # Handle block quotes
                output_file.write(f"> [!warning]- Beispiel Satz 👆🏻:\n{word}\n")
            elif len(word.strip()) >= MIN_WORD_LENGTH:  # Process words
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

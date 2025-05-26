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
    Removes German articles, cleans up the word by removing special characters,
    and extracts only the first word if multiple words are present.

    Args:
        word (str): German word potentially with article
    Returns:
        str: Cleaned word without article and only the first word
    """
    articles = [
        "jdn. / etw. ",
        "der/die ",
        "→ einem ",
        "→ einen ",
        "→ einer ",
        "→ eines ",
        "→ eine ",
        "→ etw. ",
        "→ jdn. ",
        "→ jdm. ",
        "→ sich ",
        "einem ",
        "einen ",
        "einer ",
        "eines ",
        "→ der ",
        "→ die ",
        "→ das ",
        "→ ein ",
        "= der",
        "= die",
        "= das",
        "eine ",
        "etw. ",
        "jdn. ",
        "jdm. ",
        "sich ",
        "auf ",
        "das ",
        "der ",
        "die ",
        "ein ",
        "an ",
        "= ",
        "→ ",
    ]  # List of German articles

    # Clean and normalize the word
    word = word.strip().replace("\ufeff", "").rstrip("*")

    # Extract first part before separators
    separators = [",", " - ", " -", "- ", "-"]
    for separator in separators:
        if separator in word:
            word = word.split(separator, 1)[0].strip()
            break

    # Remove article if present
    word_lower = word.lower()
    for article in articles:
        if word_lower.startswith(article):
            word = word[len(article) :].strip()
            break

    # Take only the first word if multiple words exist
    word = word.split()[0]

    return word


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

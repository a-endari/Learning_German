from deep_translator import GoogleTranslator

from audio_grabber_b_amooz import download_audio, get_audio_url
from tester2 import get_full_persian


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
    print(word.removeprefix(article).split(separator, 1)[0])  # Log
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
    persian_def = get_full_persian(base_word)

    # Format output
    output = f"> [!tldr]- {word}\n"
    if audio_url:
        output += f"> ![[{base_word}.wav]]\n"
    output += f"> {translations['en']}\n> {translations['fa']}\n{persian_def}\n"

    return output


def main():
    """Main function to process the input file and generate translations."""
    try:
        # Read input file
        with open("base.md", "r", encoding="utf-8") as basefile:
            words = basefile.readlines()

        # Process each line and write to output file
        with open("text.md", "a", encoding="utf-8") as output_file:
            for word in words:
                if word.startswith("#") or word.startswith("\ufeff#"):  # Handle headers
                    output_file.write(f"{word}\n")
                elif len(word.strip()) >= 2:  # Process words (ignore empty lines)
                    result = process_word(word) + "\n"
                    output_file.write(result)

    except FileNotFoundError:
        print("Error: Input file 'base.md' not found!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()

"""Text processing utilities for German language."""


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
        "dem",
        "den",
        "des",
        "ein ",
        "an ",
        "= ",
        "→ ",
    ]

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

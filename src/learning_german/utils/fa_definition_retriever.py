import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup


def definition_grabber(german_word: str) -> str:
    # Initialize variables
    persian_definition = ""
    synonyms_list = ""

    url = f"https://dic.b-amooz.com/de/dictionary/w?word={german_word}"

    response = requests.get(url)
    if response.status_code == 200:
        return parse_definition(response.text)
    return ""


def parse_definition(html):
    """Parse HTML to extract definition"""
    persian_definition = ""
    synonyms_list = ""
    
    soup = BeautifulSoup(html, "html.parser")
    persian_defenitions = soup.find("div", id="quick-access")

    if persian_defenitions:  # Check if definitions were found
        all_defs = persian_defenitions.find_all("span")
        my_list = [word.text.lstrip().strip() for word in all_defs]
        for i in my_list[1:-1]:
            persian_definition = persian_definition + f"> {i}\n"

    synonyms = soup.find(name="div", attrs={"class": "mt-3 mb-1"})
    if synonyms:
        # Get all text elements and clean them
        synonym_elements = synonyms.find_all(text=True)
        # Filter out '+' signs and empty strings, then strip whitespace
        clean_synonyms = [
            word.strip()
            for word in synonym_elements
            if word.strip() and word.strip() != "+"
        ]

        synonyms_list = "> **مترادف و متضاد ها:**\n> "
        # Join only the actual words with a single +
        synonyms_list += " + ".join(
            clean_synonyms[1:]
        )  # Start from index 1 to skip the header
        synonyms_list += "\n"
    return persian_definition + synonyms_list


async def definition_grabber_async(german_word: str) -> str:
    """Async version of definition_grabber"""
    # Initialize variables
    url = f"https://dic.b-amooz.com/de/dictionary/w?word={german_word}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                # Use run_in_executor for BeautifulSoup parsing as it's CPU-bound
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, parse_definition, html)
    return ""
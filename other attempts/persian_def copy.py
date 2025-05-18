import requests
from bs4 import BeautifulSoup


def definition_grabber(german_word: str) -> str:
    # Initialize variables
    persian_definition = ""
    synonyms_list = ""

    url = f"https://dic.b-amooz.com/de/dictionary/w?word={german_word}"

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select('.word-row'):
            persian = soup.select('.translation-index')
            persian_definition = persian_definition + f"> {persian.text}\n"
        

            synonyms = soup.find(name="div", attrs={"class": "mt-3 mb-1 badge-primary"})
            Antononyms = soup.find(name="div", attrs={"class": "mt-3 mb-1 badge-danger"})
            
            if synonyms:
                # Get all text elements and clean them
                synonym_elements = synonyms.find_all(text=True)
                # Filter out '+' signs and empty strings, then strip whitespace
                clean_synonyms = [word.strip() for word in synonym_elements if word.strip() and word.strip() != '+']
                
                synonyms_list = "> **مترادف و  ها:**\n> "
                # Join only the actual words with a single +
                synonyms_list += " + ".join(clean_synonyms[1:])  # Start from index 1 to skip the header
                synonyms_list += "\n"
            if Antononyms:
                # Get all text elements and clean them
                antonyms_elements = Antononyms.find_all(text=True)
                # Filter out '+' signs and empty strings, then strip whitespace
                clean_synonyms = [word.strip() for word in antonyms_elements if word.strip() and word.strip() != '+']
                antonyms_list = "> ** متضاد ها:**\n> "
                # Join only the actual words with a single +
                antonyms_list += " + ".join(clean_synonyms[1:])  # Start from index 1 to skip the header
                antonyms_list += "\n"
    return persian_definition + synonyms_list + antonyms_list + "\n"

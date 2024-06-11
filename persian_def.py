import requests
from bs4 import BeautifulSoup


def definition_grabber(german_word: str) -> str:

    url = f"https://dic.b-amooz.com/de/dictionary/w?word={german_word}"

    response = requests.get(url)
    persian_definition = ""
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        persian_defenitions = soup.find("div", id="quick-access")

        all_defs = persian_defenitions.find_all("span")
        my_list: list[str] = [word.text.lstrip().strip() for word in all_defs]
        for i in my_list[1:-1]:
            persian_definition = persian_definition + f"> {i}\n"
        return persian_definition

    return persian_definition

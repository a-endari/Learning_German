import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    # Remove excessive whitespace and normalize spaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Check if the text starts with a number followed by a dot
    number_match = re.match(r'^(\d+\.?\s*)(.*)$', text)
    if number_match:
        # Combine the number with the following text
        return f"{number_match.group(1)}{number_match.group(2)}"
    return text

def get_full_persian(word):
    final = []  # Use a list to collect lines
    url = f"https://dic.b-amooz.com/de/dictionary/w?word={word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for item in soup.select('.word-row')[:-2]:
        final.append("> ---")  # Remove extra \n
        for trab in item.find_all(string=True):
            text = clean_text(trab)
            if text:  # Only add non-empty lines
                final.append(f"> {text}")  # Remove extra \n
    return '\n'.join(final)  # Join all lines with single \n

# print(get_full_persian("nehmen"))

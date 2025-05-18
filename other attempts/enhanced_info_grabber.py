import requests
from bs4 import BeautifulSoup
import re


def extract_conjugation_info(german_word: str) -> dict:
    """
    Extracts conjugation information for German verbs.
    
    Args:
        german_word (str): The German verb to look up
        
    Returns:
        dict: Dictionary containing conjugation information
    """
    conjugation_info = {
        "present": {},
        "past": {},
        "perfect": {},
        "is_verb": False
    }
    
    # Check if the word has a conjugation page (only verbs do)
    url = f"https://dic.b-amooz.com/de/dictionary/conjugation/v?verb={german_word}"
    
    try:
        print(f"Fetching conjugation from: {url}")
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            conjugation_info["is_verb"] = True
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all conjugation tables
            tables = soup.find_all("table", class_="conjugation-table")
            print(f"Found {len(tables)} conjugation tables")
            
            # Process present tense (Präsens)
            if len(tables) > 0:
                present_rows = tables[0].find_all("tr")
                print(f"Present tense rows: {len(present_rows)}")
                
                for row in present_rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        pronoun = cells[0].text.strip()
                        form = cells[1].text.strip()
                        conjugation_info["present"][pronoun] = form
                        print(f"Present: {pronoun}: {form}")
            
            # Process past tense (Präteritum)
            if len(tables) > 2:
                past_rows = tables[2].find_all("tr")
                print(f"Past tense rows: {len(past_rows)}")
                
                for row in past_rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        pronoun = cells[0].text.strip()
                        form = cells[1].text.strip()
                        conjugation_info["past"][pronoun] = form
                        print(f"Past: {pronoun}: {form}")
            
            # Process perfect tense (Perfekt)
            if len(tables) > 1:
                perfect_rows = tables[1].find_all("tr")
                print(f"Perfect tense rows: {len(perfect_rows)}")
                
                for row in perfect_rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        pronoun = cells[0].text.strip()
                        form = cells[1].text.strip()
                        conjugation_info["perfect"][pronoun] = form
                        print(f"Perfect: {pronoun}: {form}")
                        
    except Exception as e:
        print(f"Error extracting conjugation information: {str(e)}")
    
    return conjugation_info


def extract_examples(german_word: str) -> list:
    """
    Extracts example sentences from the B-Amooz dictionary.
    
    Args:
        german_word (str): The German word to look up
        
    Returns:
        list: List of example sentences
    """
    examples = []
    
    url = f"https://dic.b-amooz.com/de/dictionary/w?word={german_word}"
    
    try:
        print(f"Fetching examples from: {url}")
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for example sentences in the page
            # Find all divs that might contain examples
            content_divs = soup.find_all("div", class_="card-body")
            print(f"Found {len(content_divs)} card-body divs")
            
            for div in content_divs:
                # Look for paragraphs that might contain examples
                paragraphs = div.find_all("p")
                print(f"Found {len(paragraphs)} paragraphs in a div")
                
                for p in paragraphs:
                    text = p.text.strip()
                    # Check if it starts with a number followed by a dot (typical example format)
                    if re.match(r'^\d+\.', text):
                        examples.append(text)
                        print(f"Found example: {text[:50]}...")
            
    except Exception as e:
        print(f"Error extracting examples: {str(e)}")
    
    return examples


def format_conjugation_info(info: dict) -> str:
    """
    Formats conjugation information into a markdown string.
    
    Args:
        info (dict): Dictionary containing conjugation information
        
    Returns:
        str: Formatted markdown string
    """
    if not info["is_verb"] or not (info["present"] or info["past"] or info["perfect"]):
        return ""
    
    output = "> **Conjugation:**\n"
    
    # Present tense
    if info["present"]:
        output += "> *Present tense:*\n"
        for pronoun, form in info["present"].items():
            output += f"> {pronoun}: {form}\n"
        output += ">\n"
    
    # Past tense
    if info["past"]:
        output += "> *Past tense:*\n"
        for pronoun, form in info["past"].items():
            output += f"> {pronoun}: {form}\n"
        output += ">\n"
    
    # Perfect tense
    if info["perfect"]:
        output += "> *Perfect tense:*\n"
        for pronoun, form in info["perfect"].items():
            output += f"> {pronoun}: {form}\n"
        output += ">\n"
    
    return output


def format_examples(examples: list) -> str:
    """
    Formats examples into a markdown string.
    
    Args:
        examples (list): List of example sentences
        
    Returns:
        str: Formatted markdown string
    """
    if not examples:
        return ""
    
    output = "> **Examples:**\n"
    for example in examples[:5]:  # Limit to 5 examples
        output += f"> - {example}\n"
    output += ">\n"
    
    return output


def get_enhanced_info(german_word: str) -> str:
    """
    Gets enhanced information about a German word including conjugation and examples.
    
    Args:
        german_word (str): The German word to look up
        
    Returns:
        str: Formatted markdown string with enhanced information
    """
    # Get conjugation information (for verbs)
    conjugation_info = extract_conjugation_info(german_word)
    conjugation_text = format_conjugation_info(conjugation_info)
    
    # Get examples
    examples = extract_examples(german_word)
    examples_text = format_examples(examples)
    
    return conjugation_text + examples_text


# For testing
if __name__ == "__main__":
    word = "nehmen"
    print(f"Testing with word: {word}")
    print(get_enhanced_info(word))
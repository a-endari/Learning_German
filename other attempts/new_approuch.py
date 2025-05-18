import requests
from bs4 import BeautifulSoup

# URL of the dictionary page
url = "https://dic.b-amooz.com/de/dictionary/w?word=nehmen"

# Send a GET request to fetch the page content
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, "html.parser")

# Prepare output for Obsidian
output = ""

# Extract the word title (with error handling)
word_title_element = soup.find("h1", class_="mdc-typography--headline4")
word_title = word_title_element.text.strip() if word_title_element else "Unknown Word"
output += f"## {word_title}\n\n"

# Extract definitions, pronunciations, and examples
definitions = soup.find_all("div", class_="word-row pos-verb-bg")

for index, definition_block in enumerate(definitions, 1):
    # Get the definition and sub-definition with error handling
    h2_element = definition_block.find("h2")
    definition_title = h2_element.text.strip() if h2_element else "No definition title"
    
    desc_element = definition_block.find("div", class_="desc")
    description = desc_element.text.strip() if desc_element else ""
    
    # Add the definition in Obsidian format
    output += f"> [!abstract]+ Definition {index}: {definition_title}\n"
    if description:
        output += f"{description}\n\n"
    
    # Extract examples
    examples = definition_block.find_all("li", class_="list-group-item")
    for example in examples:
        german_element = example.find("div", class_="prepositioned-form")
        persian_element = example.find("div", class_="prepositioned-form-translation")
        
        german_example = german_element.text.strip() if german_element else "No German example"
        persian_translation = persian_element.text.strip() if persian_element else "No translation"
        
        output += f"> - **{german_example}**: {persian_translation}\n"

# Save output to a markdown file
with open("nehmen.md", "w", encoding="utf-8") as file:
    file.write(output)

print("Data successfully exported to nehmen.md!")

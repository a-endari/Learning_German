"""
to_anki.py - Convert Obsidian callouts to Anki cards with beautiful formatting
"""

import os
import random
import re
import sys
import genanki
from learning_german.config.settings import OUTPUT_DIR
from learning_german.templates.anki_card_styles import CARD_STYLES


def extract_callouts(markdown_text):
    """Extract callouts from Obsidian markdown text and combine examples with previous cards"""
    # Pattern to match callouts like > [!tldr]- title or > [!warning]- 📝 Beispiel Satz:
    callout_pattern = r"> \[!(\w+)\]- (.*?)\n((?:>.*?\n)+)"

    # Find all callouts
    callouts = re.findall(callout_pattern, markdown_text, re.DOTALL)

    cards = []
    reverse_cards = []
    last_card = None
    last_reverse_card = None

    for callout_type, title, content in callouts:
        # Clean up the content (remove leading > and extra whitespace)
        clean_content = "\n".join(
            [line.lstrip("> ").strip() for line in content.strip().split("\n")]
        )

        # Remove audio file references like ![[filename.wav]]
        clean_content = re.sub(
            r"!\[\[.*?\.(wav|mp3|ogg)\]\]", "", clean_content
        ).strip()

        # Check if this is an example sentence - more flexible matching
        if "beispiel" in title.lower() or "📝" in title:
            # If we have a previous card, add this example to it
            if last_card and clean_content:
                # Replace newlines with <br> tags for proper HTML line breaks in examples
                formatted_example = clean_content.replace("\n", "<br>\n")

                example_content = f"""
                <div class="example">
                    <h3>📝 Example</h3>
                    <div class="example-content">{formatted_example}</div>
                </div>
                """
                # Only add the example if it doesn't already exist in the card
                if example_content not in last_card["back"]:
                    # Find the last </div> to replace (the one that closes card-content)
                    last_div_pos = last_card["back"].rfind("</div>")
                    if last_div_pos != -1:
                        last_card["back"] = (
                            last_card["back"][:last_div_pos]
                            + example_content
                            + last_card["back"][last_div_pos:]
                        )
                    else:
                        # If we can't find the closing div, just append to the end
                        last_card["back"] += example_content

                # Also add the example to the reverse card if it exists
                if (
                    last_reverse_card
                    and example_content not in last_reverse_card["back"]
                ):
                    last_div_pos = last_reverse_card["back"].rfind("</div>")
                    if last_div_pos != -1:
                        last_reverse_card["back"] = (
                            last_reverse_card["back"][:last_div_pos]
                            + example_content
                            + last_reverse_card["back"][last_div_pos:]
                        )
                    else:
                        last_reverse_card["back"] += example_content
            continue

        # Skip empty titles or contents
        if not title.strip() or not clean_content.strip():
            continue

        # Replace newlines with <br> tags for proper HTML line breaks
        formatted_content = clean_content.replace("\n", "<br>\n")

        # Create a card with title as front and content as back
        card = {
            "type": callout_type,
            "front": title.strip(),
            "back": f"""
            <div class="card-content">
                <div class="translations">{formatted_content}</div>
            </div>
            """,
        }

        cards.append(card)
        last_card = card

        # Create a reverse card with Persian as front and German as back
        # Extract the first Persian line (second line of content)
        content_lines = clean_content.split("\n")
        if len(content_lines) >= 2:  # Make sure we have at least 2 lines
            persian_text = content_lines[1].strip()

            # Create reverse card
            reverse_card = {
                "type": "reverse",
                "front": persian_text,
                "back": f"""
                <div class="card-content">
                    <div class="translations">{title.strip()}</div>
                </div>
                """,
            }

            reverse_cards.append(reverse_card)
            last_reverse_card = reverse_card

    # Remove duplicates based on front text
    seen_fronts = set()
    unique_cards = []
    
    for card in cards + reverse_cards:
        if card["front"] not in seen_fronts:
            seen_fronts.add(card["front"])
            unique_cards.append(card)
    
    return unique_cards


def create_anki_deck(cards, deck_name):
    """Create an Anki deck from the extracted cards"""
    # Generate a random model ID and deck ID
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)

    # Create a styled model for the cards
    model = genanki.Model(
        model_id,
        "Abbas Endari Language Learning Model",
        fields=[
            {"name": "Front"},
            {"name": "Back"},
        ],
        templates=[
            {
                "name": "Card",
                "qfmt": """
                <div class="front-side">
                    <div class="word">{{Front}}</div>
                </div>
                """,
                "afmt": """
                <div class="front-side">
                    <div class="word">{{Front}}</div>
                </div>
                <hr id="answer">
                <div class="back-side">
                    {{Back}}
                </div>
                """,
            },
        ],
        css=CARD_STYLES,
    )

    # Create a new deck
    deck = genanki.Deck(deck_id, deck_name)

    # Add cards to the deck
    for card_data in cards:
        note = genanki.Note(model=model, fields=[card_data["front"], card_data["back"]])
        deck.add_note(note)

    return deck


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python to_anki.py <obsidian_file1.md> [obsidian_file2.md ...] [--deck-name DECK_NAME]"
        )
        sys.exit(1)

    # Check if --deck-name flag is provided
    deck_name = None
    files = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--deck-name" and i + 1 < len(sys.argv):
            deck_name = sys.argv[i + 1]
            i += 2
        else:
            files.append(sys.argv[i])
            i += 1

    if not files:
        print("Error: No input files provided")
        sys.exit(1)

    # Process each file
    for obsidian_file in files:
        try:
            # Use the filename without extension as the deck name if not provided
            current_deck_name = (
                deck_name
                if deck_name
                else os.path.splitext(os.path.basename(obsidian_file))[0]
            )

            # Read the Obsidian file
            with open(obsidian_file, "r", encoding="utf-8") as f:
                markdown_text = f.read()

            # Extract callouts
            cards = extract_callouts(markdown_text)

            if not cards:
                print(f"No callouts found in {obsidian_file}")
                continue

            print(f"Found {len(cards)} cards to create from {obsidian_file}")

            # Create Anki deck
            deck = create_anki_deck(cards, current_deck_name)

            # Save the deck to a .apkg file
            output_file = f"{current_deck_name}.apkg"
            output_path = os.path.join(OUTPUT_DIR, output_file)
            os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the output directory exists
            genanki.Package(deck).write_to_file(output_path)

            print(f"Successfully created Anki deck: {output_path}")
            print(f"Cards created: {len(cards)}")

        except FileNotFoundError:
            print(f"Error: File {obsidian_file} not found")
        except Exception as e:
            print(f"Error processing {obsidian_file}: {str(e)}")

    print("All files processed.")


if __name__ == "__main__":
    main()

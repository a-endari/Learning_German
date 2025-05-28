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
    last_card = None

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
                example_content = f"""
                <div class="example">
                    <h3>📝 Example</h3>
                    <div class="example-content">{clean_content}</div>
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
            continue

        # Skip empty titles or contents
        if not title.strip() or not clean_content.strip():
            continue

        # Create a card with title as front and content as back
        card = {
            "type": callout_type,
            "front": title.strip(),
            "back": f"""
            <div class="card-content">
                <div class="translations" style="color: #333333;">{clean_content}</div>
            </div>
            """,
        }

        cards.append(card)
        last_card = card

    return cards


def create_anki_deck(cards, deck_name):
    """Create an Anki deck from the extracted cards"""
    # Generate a random model ID and deck ID
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)

    # Create a styled model for the cards
    model = genanki.Model(
        model_id,
        "Obsidian Callout Model",
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
        css= CARD_STYLES,
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
        print("Usage: python to_anki.py <obsidian_file.md> [deck_name]")
        sys.exit(1)

    obsidian_file = sys.argv[1]

    # Use the filename without extension as the deck name if not provided
    if len(sys.argv) > 2:
        deck_name = sys.argv[2]
    else:
        deck_name = os.path.splitext(os.path.basename(obsidian_file))[0]

    try:
        # Read the Obsidian file
        with open(obsidian_file, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        # Extract callouts
        cards = extract_callouts(markdown_text)

        if not cards:
            print(f"No callouts found in {obsidian_file}")
            sys.exit(1)

        print(f"Found {len(cards)} cards to create")

        # Create Anki deck
        deck = create_anki_deck(cards, deck_name)

        # Save the deck to a .apkg file
        output_file = f"{deck_name}.apkg"
        output_path = os.path.join(OUTPUT_DIR, output_file)
        os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the output directory exists
        genanki.Package(deck).write_to_file(output_path)

        print(f"Successfully created Anki deck: {output_path}")
        print(f"Cards created: {len(cards)}")

    except FileNotFoundError:
        print(f"Error: File {obsidian_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

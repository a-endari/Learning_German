#!/usr/bin/env python3
"""
to_anki.py - Convert Obsidian callouts to Anki cards with beautiful formatting
"""

import re
import os
import sys
import genanki
import random

def extract_callouts_with_examples(markdown_text):
    """Extract callouts from Obsidian markdown text and combine examples with previous cards"""
    # Pattern to match callouts like > [!tldr]- title or > [!warning]- Beispiel Satz 👆🏻:
    callout_pattern = r'> \[!(\w+)\]- (.*?)\n((?:>.*?\n)+)'
    
    # Find all callouts
    callouts = re.findall(callout_pattern, markdown_text, re.DOTALL)
    
    cards = []
    example_content = ""
    
    for callout_type, title, content in callouts:
        # Clean up the content (remove leading > and extra whitespace)
        clean_content = '\n'.join([line.lstrip('> ').strip() for line in content.strip().split('\n')])
        
        # Remove audio file references like ![[filename.wav]]
        clean_content = re.sub(r'!\[\[.*?\.(wav|mp3|ogg)\]\]', '', clean_content).strip()
        
        # Check if this is an example sentence
        if "Beispiel Satz 👆🏻:" in title:
            example_content = f"""
            <div class="example">
                <h3>📝 Example</h3>
                <div class="example-content">{clean_content}</div>
            </div>
            """
            # Skip creating a card for this example
            continue
            
        # Skip empty titles or contents
        if not title.strip() or not clean_content.strip():
            continue
            
        # Create a card with title as front and content as back
        cards.append({
            'type': callout_type,
            'front': title.strip(),
            'back': f"""
            <div class="card-content">
                <div class="translations">{clean_content}</div>
                {example_content}
            </div>
            """
        })
        
        # Reset example content after adding it to a card
        example_content = ""
    
    return cards

def create_anki_deck(cards, deck_name):
    """Create an Anki deck from the extracted cards"""
    # Generate a random model ID and deck ID
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)
    
    # Create a styled model for the cards
    model = genanki.Model(
        model_id,
        'Obsidian Callout Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card',
                'qfmt': '''
                <div class="front-side">
                    <div class="word">{{Front}}</div>
                </div>
                ''',
                'afmt': '''
                <div class="front-side">
                    <div class="word">{{Front}}</div>
                </div>
                <hr id="answer">
                <div class="back-side">
                    {{Back}}
                </div>
                ''',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            text-align: center;
            color: #333;
            background-color: #f8f8f8;
            padding: 20px;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .front-side .word {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .back-side {
            text-align: left;
        }
        
        .translations {
            font-size: 18px;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .example {
            background-color: #e8f4f8;
            border-left: 5px solid #3498db;
            padding: 10px 15px;
            margin-top: 15px;
            border-radius: 5px;
        }
        
        .example h3 {
            margin-top: 0;
            color: #3498db;
            font-size: 18px;
        }
        
        .example-content {
            font-size: 16px;
            line-height: 1.4;
        }
        
        hr {
            height: 1px;
            background-color: #ddd;
            border: none;
            margin: 15px 0;
        }
        '''
    )
    
    # Create a new deck
    deck = genanki.Deck(deck_id, deck_name)
    
    # Add cards to the deck
    for card_data in cards:
        note = genanki.Note(
            model=model,
            fields=[card_data['front'], card_data['back']]
        )
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
        with open(obsidian_file, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        
        # Extract callouts with examples
        cards = extract_callouts_with_examples(markdown_text)
        
        if not cards:
            print(f"No callouts found in {obsidian_file}")
            sys.exit(1)
        
        print(f"Found {len(cards)} cards to create")
        
        # Create Anki deck
        deck = create_anki_deck(cards, deck_name)
        
        # Save the deck to a .apkg file
        output_file = f"{deck_name}.apkg"
        genanki.Package(deck).write_to_file(output_file)
        
        print(f"Successfully created Anki deck: {output_file}")
        print(f"Cards created: {len(cards)}")
        
    except FileNotFoundError:
        print(f"Error: File {obsidian_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
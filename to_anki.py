#!/usr/bin/env python3
"""
to_anki.py - Convert Obsidian callouts to Anki cards with beautiful formatting
"""

import re
import os
import sys
import genanki
import random

def extract_callouts(markdown_text):
    """Extract callouts from Obsidian markdown text and combine examples with previous cards"""
    # Pattern to match callouts like > [!tldr]- title or > [!warning]- 📝 Beispiel Satz:
    callout_pattern = r'> \[!(\w+)\]- (.*?)\n((?:>.*?\n)+)'
    
    # Find all callouts
    callouts = re.findall(callout_pattern, markdown_text, re.DOTALL)
    
    cards = []
    last_card = None
    
    for callout_type, title, content in callouts:
        # Clean up the content (remove leading > and extra whitespace)
        clean_content = '\n'.join([line.lstrip('> ').strip() for line in content.strip().split('\n')])
        
        # Remove audio file references like ![[filename.wav]]
        clean_content = re.sub(r'!\[\[.*?\.(wav|mp3|ogg)\]\]', '', clean_content).strip()
        
        # Check if this is an example sentence
        if "📝 Beispiel Satz:" in title:
            # If we have a previous card, add this example to it
            if last_card and clean_content:
                example_content = f"""
                <div class="example">
                    <h3>📝 Example</h3>
                    <div class="example-content">{clean_content}</div>
                </div>
                """
                # Only add the example if it doesn't already exist in the card
                if example_content not in last_card['back']:
                    # Find the last </div> to replace (the one that closes card-content)
                    last_div_pos = last_card['back'].rfind('</div>')
                    if last_div_pos != -1:
                        last_card['back'] = last_card['back'][:last_div_pos] + example_content + last_card['back'][last_div_pos:]
            continue
            
        # Skip empty titles or contents
        if not title.strip() or not clean_content.strip():
            continue
            
        # Create a card with title as front and content as back
        card = {
            'type': callout_type,
            'front': title.strip(),
            'back': f"""
            <div class="card-content">
                <div class="translations" style="color: #333333;">{clean_content}</div>
            </div>
            """
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
            font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            text-align: center;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4eaf0 100%);
            padding: 25px;
            max-width: 600px;
            margin: 0 auto;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .front-side {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }
        
        .front-side .word {
            font-size: 26px;
            font-weight: bold;
            color: #1e88e5;
            margin-bottom: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        .back-side {
            text-align: left;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            color: #333333;
        }
        
        .translations {
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f0f8ff;
            border-radius: 8px;
            border-left: 5px solid #42a5f5;
            color: #333333;
        }
        
        .example {
            background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
            border-left: 5px solid #29b6f6;
            padding: 15px;
            margin-top: 20px;
            border-radius: 10px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        }
        
        .example h3 {
            margin-top: 0;
            color: #0277bd;
            font-size: 20px;
            font-weight: 600;
        }
        
        .example-content {
            font-size: 16px;
            line-height: 1.5;
            color: #01579b;
        }
        
        hr {
            height: 2px;
            background: linear-gradient(to right, #42a5f5, #29b6f6, #0288d1);
            border: none;
            margin: 20px 0;
            border-radius: 2px;
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
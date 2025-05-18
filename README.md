# Translate into Markdown (TiM)

A tool for creating a personal German language dictionary with pronunciation in Obsidian format.

## Overview

TiM (Translate into Markdown) is a Python script that helps language learners create a personal German dictionary with:
- English and Persian translations
- Audio pronunciation files
- Persian definitions
- Formatted output ready for Obsidian notes

## How to Format base.md

The `base.md` file is the input file where you list German words you want to process. Here's how to format it:

### Basic Format

Each word or phrase should be on a separate line:

```
der Tisch
die Katze
das Haus
```

### Special Formatting Options

1. **Headers**: Lines starting with `#` are treated as headers and passed through unchanged:
   ```
   # Animals
   der Hund
   die Katze
   ```

2. **Example Sentences**: Lines starting with `>` are treated as example sentences:
   ```
   > Ich habe einen Hund.
   ```

3. **Words with Articles**: Articles are automatically removed for audio lookup but preserved in the output:
   ```
   der Tisch  (processed as "Tisch" for audio, but displayed as "der Tisch")
   die Katze
   das Haus
   ```

4. **Words with Additional Information**: You can include additional information after commas or hyphens:
   ```
   der Tisch, table
   die Katze - cat
   ```
   The script will only process the part before the comma/hyphen.

5. **Words with Asterisks**: Asterisks at the end of words are removed:
   ```
   der Tisch*
   ```

### Examples of Valid Entries

```
# Furniture
der Tisch
die Lampe
das Bett

> Das ist ein Tisch.

der Stuhl, chair
das Fenster - window
die Tür*
```

## Output Format

The script generates a `text.md` file with:

1. **Word entries** formatted as collapsible callouts with translations:
   ```
   > [!tldr]- der Tisch
   > ![[Tisch.wav]]
   > table
   > میز
   > --- (Persian definition here)
   ```

2. **Example sentences** formatted as warning callouts:
   ```
   > [!warning]- Beispiel Satz 💡:
   > Das ist ein Tisch.
   > این یک میز است.
   ```

3. **Headers** preserved as is:
   ```
   # Furniture
   ```

## Using with Obsidian

1. Run the script to generate `text.md` and audio files in the `Media` folder
2. Copy `text.md` to your Obsidian vault
3. Copy the audio files from the `Media` folder to your Obsidian vault's media folder
4. Open the note in Obsidian to see the formatted dictionary with playable audio

## Requirements

- Python 3.6+
- Required Python packages: deep_translator, requests, beautifulsoup4
- Internet connection for translations and audio downloads

## Tips

- Keep your `base.md` file organized with headers for different categories
- Include example sentences to better understand word usage
- For best audio results, use the base form of words without articles
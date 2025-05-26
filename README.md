# Learning German Tools

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/yourusername/learning-german-tools?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/learning-german-tools?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/learning-german-tools)
![License](https://img.shields.io/github/license/yourusername/learning-german-tools)

</div>

A comprehensive toolkit for learning German that combines automated translation, audio pronunciation, and flashcard generation. This project streamlines the process of creating study materials by extracting definitions, examples, and audio from online sources and formatting them into structured markdown notes and Anki flashcards.

## ✨ Features

- 🔤 Automated translation of German words to English and Persian
- 🔊 Audio pronunciation downloads from online dictionaries
- 📚 Extraction of detailed definitions, synonyms, antonyms, and example sentences
- 📝 Markdown-formatted study notes with proper German capitalization
- 🎴 Conversion of notes to Anki flashcards with beautiful formatting
- 📋 Support for example sentences and contextual usage

## 🛠️ Components

- **TiM.py**: Translates German words into markdown format with audio and definitions
- **persian_def.py**: Extracts detailed definitions and examples from online German dictionaries
- **audio_grabber_b_amooz.py**: Downloads audio pronunciations for German words
- **to_anki.py**: Converts markdown notes to Anki flashcards with proper formatting

## 📋 Requirements

- Python 3.6+
- Required Python packages: genanki, deep_translator, requests, beautifulsoup4
- Internet connection for translations and audio downloads

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/learning-german-tools.git
   cd learning-german-tools
   ```

2. Install required dependencies:
   ```bash
   pip install genanki deep-translator requests beautifulsoup4
   ```

## 📖 Usage

### TiM.py (Translate into Markdown)

TiM (Translate into Markdown) is a Python script that helps language learners create a personal German dictionary with:
- English and Persian translations
- Audio pronunciation files
- Persian definitions
- Formatted output ready for Obsidian notes

```bash
python TiM.py
```

#### How to Format base.md

The `base.md` file is the input file where you list German words you want to process. Here's how to format it:

##### Basic Format

Each word or phrase should be on a separate line:

```
der Tisch
die Katze
das Haus
```

##### Special Formatting Options

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

#### Output Format

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
   > [!warning]- 📝 Beispiel Satz:
   > Das ist ein Tisch.
   > این یک میز است.
   ```

3. **Headers** preserved as is:
   ```
   # Furniture
   ```

### to_anki.py (Convert Markdown to Anki Flashcards)

This script converts Obsidian callouts from markdown files to Anki flashcards with beautiful formatting.

```bash
python to_anki.py <obsidian_file.md> [deck_name]
```

#### Parameters:
- `<obsidian_file.md>`: Path to the markdown file containing callouts
- `[deck_name]`: (Optional) Name for the Anki deck. If not provided, the filename without extension will be used

#### Callout Format:

The script recognizes two types of callouts:
1. Word callouts (converted to cards):
   ```
   > [!tldr]- German Word
   > ![[audio.wav]]
   > English translation
   > Persian translation
   > Additional information
   ```

2. Example sentence callouts (added to previous card):
   ```
   > [!warning]- 📝 Beispiel Satz:
   > German example sentence
   > Persian translation
   ```

#### Output:

The script generates an `.apkg` file that can be imported directly into Anki. The cards include:
- Front: German word
- Back: Translations, definitions, and example sentences
- Styling: Beautiful formatting with color-coded sections

#### Example:

```bash
python to_anki.py "2.4 Sport.md" "German Sports Vocabulary"
```

This will create a file named `German Sports Vocabulary.apkg` containing flashcards from the markdown file.

## 📱 Using with Obsidian

1. Run the script to generate `text.md` and audio files in the `Media` folder
2. Copy `text.md` to your Obsidian vault
3. Copy the audio files from the `Media` folder to your Obsidian vault's media folder
4. Open the note in Obsidian to see the formatted dictionary with playable audio

## 💡 Tips

- Keep your `base.md` file organized with headers for different categories
- Include example sentences to better understand word usage
- For best audio results, use the base form of words without articles
- Make sure German nouns and beginnings of sentences are properly capitalized in your markdown files
- Example sentences with "📝 Beispiel Satz:" will be attached to the previous card in Anki

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Genanki](https://github.com/kerrickstaley/genanki) for Anki package generation
- [Deep Translator](https://github.com/nidhaloff/deep-translator) for translation capabilities
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping
- [Obsidian](https://obsidian.md/) for markdown note-taking capabilities
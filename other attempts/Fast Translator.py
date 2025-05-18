import os
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator
from audio_grabber_b_amooz import download_audio, get_audio_url
from persian_def import definition_grabber

def remove_article(word: str) -> str:
    articles = {"der ", "die ", "der/die ", "das "}
    word_lower = word.lower()
    for article in articles:
        if word_lower.startswith(article):
            base = word_lower[len(article):].split(" -", 1)[0]
            return base.capitalize() if word.istitle() else base
    return word.split(" -", 1)[0].strip().lower()

def process_word(word_line: str) -> str:
    original_word = word_line.strip()
    if not original_word or len(original_word) < 2:
        return ""
    
    base_word = remove_article(original_word)
    
    # Get audio
    audio_url = get_audio_url(base_word)
    if audio_url:
        download_audio(audio_url, base_word)
    
    # Get translations
    try:
        en_trans = GoogleTranslator(source='de', target='en').translate(original_word)
        fa_trans = GoogleTranslator(source='de', target='fa').translate(original_word)
    except Exception as e:
        print(f"Translation failed for {original_word}: {str(e)}")
        en_trans = fa_trans = "Translation unavailable"
    
    # Get definitions
    persian_def = definition_grabber(base_word)
    
    # Build output
    output = f"> [!tldr]- {original_word}\n"
    if audio_url:
        output += f"> ![[{base_word}.wav]]\n"
    output += f"> EN: {en_trans}\n> FA: {fa_trans}\n{persian_def}\n"
    return output

def main():
    try:
        with open("base.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        processed_lines = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_map = {}
            for idx, line in enumerate(lines):
                line = line.strip()
                if line.startswith("#"):
                    processed_lines.append((idx, f"{line}\n"))
                elif len(line) >= 2:
                    future = executor.submit(process_word, line)
                    future_map[idx] = future
        
            for idx, line in sorted(future_map.items(), key=lambda x: x[0]):
                result = line.result()
                processed_lines.append((idx, result))

        # Sort all lines by original position and write
        processed_lines.sort(key=lambda x: x[0])
        with open("text.md", "w", encoding="utf-8") as f:
            for _, content in processed_lines:
                f.write(content + "\n")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
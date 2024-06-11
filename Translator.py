from deep_translator import GoogleTranslator

from audio_grabber import download_audio, get_audio_url


def remove_prefix(word: str):
    if word.lower().startswith("der "):
        return word.lower().removeprefix("der ").title()
    elif word.lower().startswith("die "):
        return word.lower().removeprefix("die ").title()
    elif word.lower().startswith("das "):
        return word.lower().removeprefix("das ").title()
    else:
        return word


with open("base.md", "r", encoding="utf-8") as basefile:
    words = basefile.readlines()
for word in words:
    if word.startswith("#"):
        with open("text.md", "a", encoding="utf-8") as output_file:
            output_file.write(f"{word}\n")
    elif len(word) < 2:
        pass
    else:
        word_to_translate = word.removesuffix("\n")
        word_for_audio = remove_prefix(word_to_translate)
        audio_url = get_audio_url(word_for_audio)
        if audio_url:
            download_audio(audio_url, filename=word_to_translate)
        else:
            print(f"Audio file for {word_for_audio} not found!")
        translation_en = GoogleTranslator(source="de", target="en").translate(
            text=word_to_translate
        )
        translation_fa = GoogleTranslator(source="de", target="fa").translate(
            text=word_to_translate
        )
        with open("text.md", "a", encoding="utf-8") as output_file:
            if audio_url:
                output_file.write(
                    f"> [!tldr]- {word_to_translate}\n> ![[{word_to_translate}.ogg]]\n> {translation_en}\n> {translation_fa}\n\n"
                )
            else:
                output_file.write(
                    f"> [!tldr]- {word_to_translate}\n> {translation_en}\n> {translation_fa}\n\n"
                )

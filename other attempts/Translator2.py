from deep_translator import GoogleTranslator

from audio_grabber_b_amooz import download_audio, get_audio_url
from persian_def import definition_grabber


def remove_prefix(word: str):
    seperator = " -"
    if word.lower().startswith("der "):
        new = word.lower().removeprefix("der ")
        return new.split(seperator, 1)[0]
    elif word.lower().startswith("die "):
        new = word.lower().removeprefix("die ")
        return new.split(seperator, 1)[0]
    elif word.lower().startswith("der/die "):
        new = word.lower().removeprefix("der/die ")
        return new.split(seperator, 1)[0]
    elif word.lower().startswith("das "):
        new = word.lower().removeprefix("das ")
        return new.split(seperator, 1)[0]
    else:
        new = word.title()
        return new.split(seperator, 1)[0]


with open(file="base.md", mode="r", encoding="utf-8") as basefile:
    all_words = basefile.readlines()
for word in all_words:
    if word.startswith("#"):
        with open("text.md", "a", encoding="utf-8") as output_file:
            output_file.write(f"{word}\n")
    elif len(word) < 2:
        pass
    else:
        word_to_translate = word.removesuffix("\n")
        name_of_audio_file = remove_prefix(word_to_translate)
        audio_url = get_audio_url(name_of_audio_file)
        persian_def = definition_grabber(name_of_audio_file)
        if audio_url:
            download_audio(audio_url, filename=name_of_audio_file)
        else:
            print(f"Audio file for {name_of_audio_file} not found!")
        translation_en = GoogleTranslator(source="de", target="en").translate(
            text=word_to_translate
        )
        translation_fa = GoogleTranslator(source="de", target="fa").translate(
            text=word_to_translate
        )
        with open("text.md", "a", encoding="utf-8") as output_file:
            if audio_url:
                output_file.write(
                    f"> [!tldr]- {word_to_translate}\n> ![[{name_of_audio_file}.wav]]\n> {translation_en}\n> {translation_fa}\n{persian_def}\n"
                )
            else:
                output_file.write(
                    f"> [!tldr]- {word_to_translate}\n> {translation_en}\n> {translation_fa}\n{persian_def}\n"
                )

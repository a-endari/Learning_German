# import fitz
from deep_translator import GoogleTranslator  # type: ignore

with open("base.txt", "r") as basefile:
    words = basefile.readlines()

for word in words:
    word_to_translate = word.removesuffix("\n")
    translation_en = GoogleTranslator(source="de", target="en").translate(
        text=word_to_translate
    )
    translation_fa = GoogleTranslator(source="de", target="fa").translate(
        text=word_to_translate
    )
    with open("text.md", "a", encoding="utf-8") as output_file:
        output_file.write(
            f"> **{word_to_translate}** ➡ {translation_en} , {translation_fa}\n\n"
        )

from deep_translator import GoogleTranslator

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
            f"> [!NOTE]- {word_to_translate}\n> {translation_en} \n> {translation_fa}\n\n"
        )

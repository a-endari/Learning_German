# import fitz
from deep_translator import GoogleTranslator

# doc = fitz.open("a13.pdf")


# highlights_cords = []
# all_h_words = []
# for page in doc:
#     all_page_words = page.get_text_words()
#     for annot in page.annots():
#         anot_vert = annot.vertices
#         print(annot.type)
#         highlight_coord = fitz.Quad(anot_vert).rect
#         highlights_cords.append(highlight_coord)
#     for word in all_page_words:
#         if fitz.Rect(word[0:4]).include_rect(
#             highlight_coord
#         ):  ### here needs work some how!!!!
#             # intersect(highlight_coord):
#             all_h_words.append(word[4])
# print(len(all_h_words))
### Translation and adding to .md file (works like acharm.)

with open("base.txt", "r") as basefile:
    words = basefile.readlines()

for word in words:
    word_to_translate = word.removesuffix("\n")
    translation = GoogleTranslator(source="de", target="en").translate(
        text=word_to_translate
    )
    translation_fa = GoogleTranslator(source="de", target="fa").translate(
        text=word_to_translate
    )
    with open("text.md", "a", encoding="utf-8") as output_file:
        output_file.write(
            f"> **{word_to_translate}** ➡ {translation} , {translation_fa}\n\n"
        )

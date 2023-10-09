from fitz import open as pdfopen


file = pdfopen("a13.pdf")

# print(dir(file))
print(file.metadata)

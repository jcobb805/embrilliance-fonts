import pypdfium2 as pdfium
from pathlib import Path

src = Path(__file__).parent / "Fonts.pdf"
out = Path(__file__).parent / "pages"
out.mkdir(exist_ok=True)

pdf = pdfium.PdfDocument(str(src))
print(f"Pages: {len(pdf)}")
for i, page in enumerate(pdf):
    pil = page.render(scale=2.0).to_pil()
    pil.save(out / f"page_{i+1}.png")
    print(f"  page {i+1}: {pil.size}")

"""Build the public CV PDF and a private application copy from the current CV."""

from html import escape
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HTML = ROOT / "cv" / "index.html"
PUBLIC_PDF = ROOT / "cv" / "kathryn-hopkins-data-scientist.pdf"
PRIVATE_CV_DIR = ROOT.parents[2] / "KH CVs"
SOURCE_DOCX = PRIVATE_CV_DIR / "Kathryn Hopkins - Data Scientist.docx"
PRIVATE_PDF = PRIVATE_CV_DIR / "Kathryn Hopkins - Data Scientist.pdf"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+44\s*(?:\(0\)\s*)?|0)(?:[\s().-]*\d){9,10}(?!\d)")


def application_email():
    with zipfile.ZipFile(SOURCE_DOCX) as document:
        xml = ET.fromstring(document.read("word/document.xml"))
    text = " ".join(node.text or "" for node in xml.iter(f"{{{WORD_NS}}}t"))
    emails = sorted(set(EMAIL_RE.findall(text)))
    if len(emails) != 1:
        raise ValueError(f"Expected one email address in {SOURCE_DOCX.name}; found {len(emails)}")
    return emails[0]


def render_pdf(fitz, source, destination, title):
    story = fitz.Story(html=source)
    paper = fitz.paper_rect("a4")
    content = fitz.Rect(43, 42, paper.width - 43, paper.height - 44)
    pdf = story.write_with_links(lambda index, filled: (paper, content, None))
    for index, page in enumerate(pdf):
        page.insert_text((43, paper.height - 24), "Kathryn Hopkins · Data Scientist", fontsize=8, color=(.33, .4, .43))
        page.insert_text((paper.width - 54, paper.height - 24), str(index + 1), fontsize=8, color=(.33, .4, .43))
    pdf.set_metadata({"title": title, "author": "Kathryn Hopkins"})
    pdf.save(destination)
    text = "\n".join(page.get_text() for page in pdf)
    if "Kathryn Hopkins" not in text or "Environmental Science" not in text:
        raise ValueError(f"Generated PDF is missing expected CV content: {destination}")
    return text, len(pdf)


def pdf_source(source):
    source = re.sub(r'<header class="shell cv-header">.*?</header>', "", source, flags=re.DOTALL)
    source = re.sub(r'<footer class="cv-footer">.*?</footer>', "", source, flags=re.DOTALL)
    source = source.replace("</head>", "<style>h1 { font-size: 40px; } .strapline { font-size: 13px; white-space: nowrap; }</style></head>", 1)
    return source


def main():
    sys.path.insert(0, str(ROOT.parent / "CV Review" / ".tools"))
    import pymupdf as fitz

    public_html = PUBLIC_HTML.read_text(encoding="utf-8")
    if EMAIL_RE.search(public_html):
        raise ValueError("The public CV HTML must not contain an email address")
    if PHONE_RE.search(public_html):
        raise ValueError("The public CV HTML must not contain a phone number")
    marker = "<!-- Application-only email is added by the local PDF builder. -->"
    if public_html.count(marker) != 1:
        raise ValueError("The CV contact marker is missing or duplicated")
    email = application_email()
    private_html = public_html.replace(
        marker,
        f'<p class="cv-contact">Email: <a href="mailto:{escape(email, quote=True)}">{escape(email)}</a></p>',
    )

    public_text, public_pages = render_pdf(fitz, pdf_source(public_html), PUBLIC_PDF, "Kathryn Hopkins — Data Scientist")
    private_text, private_pages = render_pdf(fitz, pdf_source(private_html), PRIVATE_PDF, "Kathryn Hopkins — Data Scientist")
    if EMAIL_RE.search(public_text):
        raise ValueError("The public CV PDF contains an email address")
    if PHONE_RE.search(public_text):
        raise ValueError("The public CV PDF contains a phone number")
    if email not in private_text:
        raise ValueError("The application PDF does not contain the source CV email address")
    print(f"Public CV PDF: {PUBLIC_PDF} ({public_pages} pages)")
    print(f"Application CV PDF: {PRIVATE_PDF} ({private_pages} pages)")


if __name__ == "__main__":
    main()
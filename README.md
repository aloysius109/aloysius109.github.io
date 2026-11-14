# aloysius109.github.io

[Visit the live portfolio homepage](https://aloysius109.github.io/)

Homepage for pinned reports and research publications, with a redacted public CV.

Shared social preview cards are stored in `assets/og/`; the favicon files are at the site root. Regenerate them with `python scripts/make_social_cards.py` (requires Matplotlib and Pillow). The report sites reference these assets from the portfolio's public origin.

The public CV at `cv/index.html` is the content master and omits personal contact details. Its downloadable PDF and the full application PDF are both generated from that page with `python scripts/build_cv_pdf.py`; the script reads only the application email from `Documents/KH CVs\Kathryn Hopkins - Data Scientist.docx` and writes the full application PDF there. The Word document is a separate format copy for application portals that require `.docx`, not the content source. The public PDF is part of this repository; the private application PDF is not.

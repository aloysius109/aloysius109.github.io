# aloysius109.github.io

[Visit the live portfolio homepage](https://aloysius109.github.io/)

Homepage for pinned reports and research publications, with a redacted public CV.

Shared social preview cards are stored in `assets/og/`; the favicon files are at the site root. Regenerate them with `python scripts/make_social_cards.py` (requires Matplotlib and Pillow). The report sites reference these assets from the portfolio's public origin.

The public CV is `cv/index.html`; it omits personal contact details and links to the GitHub profile. Build its downloadable PDF with `python scripts/build_cv_pdf.py`. The script reads the application email from the current CV under `Documents/KH CVs` and writes the full application PDF there; that private PDF is not part of this repository.

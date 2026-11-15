# aloysius109.github.io

[Visit the live portfolio homepage](https://aloysius109.github.io/)

Homepage for pinned reports and research publications, with a redacted public CV.

Shared social preview cards are stored in `assets/og/`; the favicon files are at the site root. Regenerate them with `python scripts/make_social_cards.py` (requires Matplotlib and Pillow). The report sites reference these assets from the portfolio's public origin.

The public CV at `cv/index.html` is the content master and omits personal contact details. Its downloadable PDF and the full application PDF are both generated from that page with `python scripts/build_cv_pdf.py`; the script reads only the application email from `Documents/KH CVs\Kathryn Hopkins - Data Scientist.docx` and writes the full application PDF there. The Word document is a separate format copy for application portals that require `.docx`, not the content source. The public PDF is part of this repository; the private application PDF is not.

The portfolio uses GoatCounter. Its account URL is defined once as `GOATCOUNTER_URL` in `scripts/build_feed.py`; change that constant and rerun the script to synchronize `index.html`, `cv/index.html` and `404.html`. GoatCounter is used without cookies, a consent banner or personal-data collection.

The homepage footer links to the public readership dashboard at <https://aloysius109.goatcounter.com/>. That link only works while **Dashboard viewable by** on the [GoatCounter Main settings](https://aloysius109.goatcounter.com/settings/main) page allows anyone to view it; this is a setting on the Main page, not a separate “Public dashboard” checkbox. If the dashboard is ever made private again, remove the `Portfolio readership` link from `index.html`, or visitors are sent to a login page.

When adding or changing a report card in `index.html`, run `python scripts/build_feed.py` before committing. The generator updates `feed.xml`, `sitemap.xml`, the JSON-LD blocks, and the portfolio-page tracking snippets from their sources.

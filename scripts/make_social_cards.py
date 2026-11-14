"""Generate the portfolio's shared social preview cards and favicon assets."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Rectangle
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CARD_SIZE = (1200, 630)

PAPER = "#f4f8fb"
INK = "#26352e"
MUTED = "#68756e"
GREEN = "#496b58"

CARDS = [
    {
        "slug": "portfolio",
        "kicker": "KATHRYN HOPKINS  ·  INDEPENDENT RESEARCH",
        "title": "Data, in context.",
        "description": "Data science, independent research and\ndata-led stories by Kathryn Hopkins.",
        "metric": "06",
        "metric_label": "published reports",
        "accent": GREEN,
        "tint": "#edf2ec",
    },
    {
        "slug": "asylum",
        "kicker": "GLOBAL ASYLUM  ·  UNHCR DATA",
        "title": "Asylum in\nperspective",
        "description": "A reader's guide to worldwide applications,\ndecisions and pending claims.",
        "metric": "9.0m",
        "metric_label": "people in observed asylum-seeker stock",
        "accent": "#28686b",
        "tint": "#e8f1ee",
    },
    {
        "slug": "predictive",
        "kicker": "INTERACTIVE MODEL  ·  EXPLORATORY",
        "title": "Explore asylum\noutcomes",
        "description": "Compare modelled decision outcomes by origin,\ncountry of asylum and year.",
        "metric": "4",
        "metric_label": "modelled decision outcomes",
        "accent": "#a9677d",
        "tint": "#f8e9ed",
    },
    {
        "slug": "sexual-violence",
        "kicker": "WORLDWIDE EVIDENCE  ·  UK DETAIL",
        "title": "Sexual violence\nin perspective",
        "description": "Careful comparisons across measures,\npopulations and data sources.",
        "metric": "138",
        "metric_label": "countries with WHO estimates",
        "accent": "#365d71",
        "tint": "#edf5f8",
    },
    {
        "slug": "housing",
        "kicker": "HOUSING AFFORDABILITY  ·  ENGLAND & WALES",
        "title": "The affordability\nsqueeze",
        "description": "House prices still take years of earnings\nto reach, despite recent easing.",
        "metric": "8.03x",
        "metric_label": "median local-authority ratio in 2025",
        "accent": GREEN,
        "tint": "#f1f2e8",
    },
    {
        "slug": "ev",
        "kicker": "PUBLIC EV CHARGING  ·  UNITED KINGDOM",
        "title": "Where the UK\nplugs in",
        "description": "Charger coverage is spreading, but reach\nand speed still vary by place.",
        "metric": "121,171",
        "metric_label": "public EV chargers · July 2026",
        "accent": "#417b6b",
        "tint": "#e9f2ed",
    },
    {
        "slug": "spacex",
        "kicker": "SPACEX  ·  APPLIED MACHINE LEARNING",
        "title": "Can we predict a\nbooster landing?",
        "description": "Launch outcomes, recovery trends and a\ncareful look at model performance.",
        "metric": "90",
        "metric_label": "Falcon 9 launches in the analysis set",
        "accent": "#355e80",
        "tint": "#eaf1f7",
    },
]


def draw_card(card):
    fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=PAPER)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.add_patch(Rectangle((0, 0), 1, 1, color=PAPER))
    ax.add_patch(Rectangle((0, 0), 0.012, 1, color=card["accent"]))
    ax.add_patch(Rectangle((0.69, 0), 0.31, 1, color=card["tint"]))
    ax.add_patch(Circle((0.91, 0.66), 0.25, facecolor="none", edgecolor=card["accent"], linewidth=1.3, alpha=0.25))
    ax.add_patch(Circle((0.91, 0.66), 0.17, facecolor="none", edgecolor=card["accent"], linewidth=1.3, alpha=0.2))
    ax.add_patch(Circle((0.91, 0.66), 0.085, facecolor=card["accent"], edgecolor="none", alpha=0.08))
    ax.add_patch(Rectangle((0.76, 0.16), 0.18, 0.006, color=card["accent"], alpha=0.2))
    for index, height in enumerate((0.045, 0.075, 0.105, 0.135)):
        ax.add_patch(
            Rectangle(
                (0.77 + index * 0.045, 0.16),
                0.025,
                height,
                color=card["accent"],
                alpha=0.28 + index * 0.12,
            )
        )

    ax.text(0.075, 0.88, card["kicker"], color=card["accent"], fontsize=11, fontweight="bold", va="top")
    title_size = 48 if "\n" in card["title"] else 56
    ax.text(
        0.075,
        0.72,
        card["title"],
        color=INK,
        fontsize=title_size,
        fontweight="bold",
        linespacing=1.08,
        va="top",
    )
    ax.text(0.078, 0.36, card["description"], color=MUTED, fontsize=17, linespacing=1.55, va="top")
    ax.text(0.075, 0.09, "KATHRYN HOPKINS  ·  DATA, IN CONTEXT", color=GREEN, fontsize=10, fontweight="bold", va="bottom")
    ax.text(0.94, 0.09, "aloysius109.github.io", color=MUTED, fontsize=10, ha="right", va="bottom")

    metric_size = 43 if len(card["metric"]) > 5 else 54
    ax.text(0.845, 0.52, card["metric"], color=card["accent"], fontsize=metric_size, fontweight="bold", ha="center", va="center")
    ax.text(0.845, 0.39, card["metric_label"], color=INK, fontsize=11, ha="center", va="top", wrap=True)

    destination = ASSETS / "og" / f"{card['slug']}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=100, facecolor=PAPER)
    plt.close(fig)
    with Image.open(destination) as image:
        if image.size != CARD_SIZE:
            raise ValueError(f"Unexpected social card dimensions for {destination}: {image.size}")
        image.save(destination, format="PNG", optimize=True)


def write_icons():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="16" fill="#496b58"/>
  <text x="32" y="46" fill="#ffffff" font-family="Arial,sans-serif" font-size="44" font-weight="700" text-anchor="middle">K</text>
</svg>
'''
    (ROOT / "favicon.svg").write_text(svg, encoding="utf-8")

    icon_font = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
    image = Image.new("RGB", (180, 180), GREEN)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(icon_font, 126)
    bounds = draw.textbbox((0, 0), "K", font=font)
    x = (180 - (bounds[2] - bounds[0])) / 2 - bounds[0]
    y = (180 - (bounds[3] - bounds[1])) / 2 - bounds[1] - 4
    draw.text((x, y), "K", fill="white", font=font)
    image.save(ROOT / "apple-touch-icon.png", format="PNG", optimize=True)
    image.resize((48, 48), Image.Resampling.LANCZOS).save(
        ROOT / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )


def main():
    for card in CARDS:
        draw_card(card)
    write_icons()
    for path in sorted((ASSETS / "og").glob("*.png")):
        print(f"{path.relative_to(ROOT)}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
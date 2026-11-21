"""Generate GitHub repository social preview images in the portfolio card style.

GitHub recommends 1280 x 640 pixels with a 40 pt (80 px) border that may be
cropped, so every piece of text stays inside that safe area. Upload each image
under the repository's Settings > General > Social preview.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from PIL import Image

from make_social_cards import CARDS, GREEN, INK, MUTED, PAPER


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "repo-previews"
WIDTH, HEIGHT = 1280, 640
SAFE = 80
PANEL_X = 880
MAX_BYTES = 1_000_000

REPOS = {
    "aloysius109.github.io": "portfolio",
    "asylum-tracker": "asylum",
    "ev-charger-report": "ev",
    "housing-affordability-report": "housing",
    "predictive-analytics": "predictive",
    "sexual-violence-report": "sexual-violence",
    "uk-asylum": "uk-asylum",
}


def balanced(label, width=32):
    if len(label) <= width:
        return label
    words = label.split()
    splits = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
    return "\n".join(min(splits, key=lambda lines: max(map(len, lines))))


def check_inside(fig, artist, left, right, name):
    box = artist.get_window_extent(fig.canvas.get_renderer())
    top, bottom = HEIGHT - box.y1, HEIGHT - box.y0
    if box.x0 < left or box.x1 > right or top < SAFE or bottom > HEIGHT - SAFE:
        raise ValueError(f"{name} text falls outside its area: {box}")


def draw_preview(repo, card):
    fig = plt.figure(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100, facecolor=PAPER)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.axis("off")

    accent = card["accent"]
    ax.add_patch(Rectangle((0, 0), WIDTH, HEIGHT, color=PAPER))
    ax.add_patch(Rectangle((0, 0), 16, HEIGHT, color=accent))
    ax.add_patch(Rectangle((PANEL_X, 0), WIDTH - PANEL_X, HEIGHT, color=card["tint"]))
    centre = (PANEL_X + WIDTH - SAFE) / 2
    for radius, alpha in ((150, 0.25), (105, 0.2)):
        ax.add_patch(Circle((centre, 440), radius, facecolor="none", edgecolor=accent, linewidth=1.3, alpha=alpha))
    ax.add_patch(Circle((centre, 440), 55, facecolor=accent, edgecolor="none", alpha=0.08))
    ax.add_patch(Rectangle((centre - 100, 140), 200, 4, color=accent, alpha=0.2))
    for index, height in enumerate((24, 38, 52, 66)):
        ax.add_patch(Rectangle((centre - 88 + index * 50, 140), 28, height, color=accent, alpha=0.28 + index * 0.12))

    texts = [
        ("kicker", ax.text(112, 540, card["kicker"], color=accent, fontsize=11, fontweight="bold", va="top"), PANEL_X - 30),
        (
            "title",
            ax.text(
                112,
                468,
                card["title"],
                color=INK,
                fontsize=48 if "\n" in card["title"] else 56,
                fontweight="bold",
                linespacing=1.08,
                va="top",
            ),
            PANEL_X - 20,
        ),
        ("description", ax.text(114, 262, card["description"], color=MUTED, fontsize=17, linespacing=1.55, va="top"), PANEL_X - 30),
        ("signature", ax.text(112, 90, "KATHRYN HOPKINS  ·  DATA, IN CONTEXT", color=GREEN, fontsize=10, fontweight="bold", va="bottom"), PANEL_X - 30),
    ]
    metric_size = 43 if len(card["metric"]) > 5 else 54
    texts += [
        ("metric", ax.text(centre, 330, card["metric"], color=accent, fontsize=metric_size, fontweight="bold", ha="center", va="center"), WIDTH - SAFE),
        (
            "metric label",
            ax.text(
                centre,
                262,
                balanced(card["metric_label"]),
                color=INK,
                fontsize=11,
                linespacing=1.4,
                ha="center",
                va="top",
                multialignment="center",
            ),
            WIDTH - SAFE,
        ),
        ("repository", ax.text(centre, 90, f"aloysius109/{repo}", color=MUTED, fontsize=10, ha="center", va="bottom"), WIDTH - SAFE),
    ]

    fig.canvas.draw()
    for name, artist, right in texts:
        left = PANEL_X + 10 if right == WIDTH - SAFE else SAFE
        check_inside(fig, artist, left, right, f"{repo} {name}")

    destination = OUTPUT / f"{repo}.png"
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=100, facecolor=PAPER)
    plt.close(fig)
    with Image.open(destination) as image:
        if image.size != (WIDTH, HEIGHT):
            raise ValueError(f"Unexpected preview dimensions for {destination}: {image.size}")
        image.save(destination, format="PNG", optimize=True)
    if destination.stat().st_size >= MAX_BYTES:
        raise ValueError(f"{destination} is over GitHub's 1 MB social preview limit")
    return destination


def main():
    cards = {card["slug"]: card for card in CARDS}
    for repo, slug in REPOS.items():
        path = draw_preview(repo, cards[slug])
        print(f"{path.relative_to(ROOT)}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

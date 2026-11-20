"""Build the portfolio Atom feed, sitemap, and structured data from its cards."""
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CV = ROOT / "cv" / "index.html"
FEED = ROOT / "feed.xml"
SITEMAP = ROOT / "sitemap.xml"
SITE_URL = "https://aloysius109.github.io/"
GOATCOUNTER_URL = "https://aloysius109.goatcounter.com/count"
ATOM_NS = "http://www.w3.org/2005/Atom"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
JSONLD_START = "<!-- json-ld:start -->"
JSONLD_END = "<!-- json-ld:end -->"
GOATCOUNTER_PATTERN = re.compile(
    r'<script\s+data-goatcounter="[^"]+"\s+async\s+src="//gc\.zgo\.at/count\.js"></script>'
)


@dataclass(frozen=True)
class ReportCard:
    url: str
    title: str
    summary: str
    published: date
    updated: date
    tags: list[str]


class ReportCardsParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards = []
        self.current = None
        self.captures = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())
        if self.current is None and tag in {"a", "article"} and "report-card" in classes:
            self.current = {
                "attrs": attributes,
                "label": attributes.get("aria-label", ""),
                "card_tag": tag,
                "title": [],
                "summary": [],
                "tags": [],
            }
            return
        if self.current is None:
            return
        if "report-title" in classes:
            self.captures.append((tag, "title", []))
        elif "report-description" in classes:
            self.captures.append((tag, "summary", []))
        elif "tag" in classes:
            self.captures.append((tag, "tag", []))

    def handle_data(self, data):
        if self.current is not None and self.captures:
            self.captures[-1][2].append(data)

    def handle_endtag(self, tag):
        if self.current is None:
            return
        if self.captures and self.captures[-1][0] == tag:
            _, field, parts = self.captures.pop()
            text = normalize_text("".join(parts))
            if field == "tag":
                if text:
                    self.current["tags"].append(text)
            else:
                self.current[field].append(text)
        if tag == self.current["card_tag"]:
            self._finish_card()

    def close(self):
        super().close()
        if self.current is not None:
            raise ValueError(f"Unclosed report card: {self.current['label'] or 'card ' + str(len(self.cards) + 1)}")

    def _finish_card(self):
        record = self.current
        self.current = None
        self.captures.clear()
        label = record["label"] or f"card {len(self.cards) + 1}"
        attrs = record["attrs"]
        required = {
            "data-report-url or href": attrs.get("data-report-url") or attrs.get("href"),
            "data-published": attrs.get("data-published"),
            "data-updated": attrs.get("data-updated"),
            ".report-title": " ".join(record["title"]),
            ".report-description": " ".join(record["summary"]),
        }
        missing = [field for field, value in required.items() if not value]
        if missing:
            raise ValueError(f"Report {label} is missing required fields: {', '.join(missing)}")

        url = (attrs.get("data-report-url") or attrs.get("href")).strip()
        parsed_url = urlsplit(url)
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise ValueError(f"Report {label} must have an absolute HTTPS URL: {url}")
        try:
            published = date.fromisoformat(attrs["data-published"])
            updated = date.fromisoformat(attrs["data-updated"])
        except ValueError as error:
            raise ValueError(f"Report {label} has an invalid ISO publication date") from error
        if updated < published:
            raise ValueError(f"Report {label} has an update date before its publication date")

        self.cards.append(ReportCard(
            url=url,
            title=normalize_text(" ".join(record["title"])),
            summary=normalize_text(" ".join(record["summary"])),
            published=published,
            updated=updated,
            tags=record["tags"],
        ))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_cards(html: str) -> list[ReportCard]:
    parser = ReportCardsParser()
    parser.feed(html)
    parser.close()
    if not parser.cards:
        raise ValueError("No .report-card elements with publication dates were found")
    urls = [card.url for card in parser.cards]
    if len(urls) != len(set(urls)):
        raise ValueError("Report card URLs must be unique")
    return parser.cards


def read_cards(index_html: Path) -> list[ReportCard]:
    return parse_cards(index_html.read_text(encoding="utf-8"))


def rfc3339(value: date) -> str:
    return f"{value.isoformat()}T00:00:00Z"


def atom_document(cards: list[ReportCard]) -> ET.Element:
    ET.register_namespace("", ATOM_NS)
    feed = ET.Element(f"{{{ATOM_NS}}}feed")
    ET.SubElement(feed, f"{{{ATOM_NS}}}id").text = SITE_URL + "feed.xml"
    ET.SubElement(feed, f"{{{ATOM_NS}}}title").text = "Kathryn Hopkins — Data, in context"
    ET.SubElement(feed, f"{{{ATOM_NS}}}subtitle").text = "New reports and research publications by Kathryn Hopkins."
    ET.SubElement(feed, f"{{{ATOM_NS}}}updated").text = rfc3339(max(card.updated for card in cards))
    ET.SubElement(feed, f"{{{ATOM_NS}}}link", {"rel": "self", "href": SITE_URL + "feed.xml"})
    ET.SubElement(feed, f"{{{ATOM_NS}}}link", {"rel": "alternate", "href": SITE_URL})
    author = ET.SubElement(feed, f"{{{ATOM_NS}}}author")
    ET.SubElement(author, f"{{{ATOM_NS}}}name").text = "Kathryn Hopkins"
    ET.SubElement(author, f"{{{ATOM_NS}}}uri").text = SITE_URL

    for card in cards:
        entry = ET.SubElement(feed, f"{{{ATOM_NS}}}entry")
        ET.SubElement(entry, f"{{{ATOM_NS}}}id").text = card.url
        ET.SubElement(entry, f"{{{ATOM_NS}}}title").text = card.title
        ET.SubElement(entry, f"{{{ATOM_NS}}}summary").text = card.summary
        ET.SubElement(entry, f"{{{ATOM_NS}}}published").text = rfc3339(card.published)
        ET.SubElement(entry, f"{{{ATOM_NS}}}updated").text = rfc3339(card.updated)
        ET.SubElement(entry, f"{{{ATOM_NS}}}link", {"href": card.url, "rel": "alternate"})
        for tag in card.tags:
            ET.SubElement(entry, f"{{{ATOM_NS}}}category", {"term": tag})
    return feed


def xml_bytes(root: ET.Element) -> bytes:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def write_atom(cards: list[ReportCard], out: Path) -> None:
    out.write_bytes(xml_bytes(atom_document(cards)))


def sitemap_document(cards: list[ReportCard]) -> ET.Element:
    ET.register_namespace("", SITEMAP_NS)
    urlset = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    latest = max(card.updated for card in cards)
    urls = [(SITE_URL, latest), (SITE_URL + "cv/", latest)]
    urls.extend((card.url, card.updated) for card in cards)
    for location, lastmod in urls:
        url = ET.SubElement(urlset, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(url, f"{{{SITEMAP_NS}}}loc").text = location
        ET.SubElement(url, f"{{{SITEMAP_NS}}}lastmod").text = lastmod.isoformat()
    return urlset


def write_sitemap(cards: list[ReportCard], out: Path) -> None:
    out.write_bytes(xml_bytes(sitemap_document(cards)))


def person_jsonld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": SITE_URL + "#person",
        "name": "Kathryn Hopkins",
        "jobTitle": "Data Scientist",
        "url": SITE_URL,
        "sameAs": ["https://github.com/aloysius109"],
    }


def index_jsonld(cards: list[ReportCard]) -> dict:
    item_list = {
        "@type": "ItemList",
        "@id": SITE_URL + "#reports",
        "name": "Selected reports by Kathryn Hopkins",
        "numberOfItems": len(cards),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "item": {
                    "@type": "CreativeWork",
                    "name": card.title,
                    "description": card.summary,
                    "url": card.url,
                },
            }
            for position, card in enumerate(cards, start=1)
        ],
    }
    return {"@context": "https://schema.org", "@graph": [person_jsonld(), item_list]}


def jsonld_block(payload: dict) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    serialized = serialized.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    serialized = "\n".join("    " + line for line in serialized.splitlines())
    return f"  {JSONLD_START}\n  <script type=\"application/ld+json\">\n{serialized}\n  </script>\n  {JSONLD_END}"


def inject_jsonld(path: Path, payload: dict) -> None:
    text = path.read_text(encoding="utf-8")
    starts = text.count(JSONLD_START)
    ends = text.count(JSONLD_END)
    block = jsonld_block(payload)
    if starts == 0 and ends == 0:
        head_end = text.find("</head>")
        if head_end < 0:
            raise ValueError(f"Cannot inject JSON-LD into {path}: </head> not found")
        text = text[:head_end] + block + "\n" + text[head_end:]
    elif starts == 1 and ends == 1:
        start = text.index(JSONLD_START)
        end = text.index(JSONLD_END)
        if start >= end:
            raise ValueError(f"JSON-LD sentinels are out of order in {path}")
        start_line = text.rfind("\n", 0, start) + 1
        end_line = text.find("\n", end)
        if end_line < 0:
            end_line = len(text)
        else:
            end_line += 1
        text = text[:start_line] + block + "\n" + text[end_line:]
    else:
        raise ValueError(f"Expected either zero or one complete JSON-LD sentinel pair in {path}")
    path.write_text(text, encoding="utf-8", newline="\n")


def inject_analytics(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    matches = list(GOATCOUNTER_PATTERN.finditer(text))
    if len(matches) > 1:
        raise ValueError(f"Expected at most one GoatCounter snippet in {path}, found {len(matches)}")
    snippet = (
        f'<script data-goatcounter="{GOATCOUNTER_URL}"\n'
        '          async src="//gc.zgo.at/count.js"></script>'
    )
    if matches:
        match = matches[0]
        text = text[:match.start()] + snippet + text[match.end():]
    else:
        body_end = text.find("</body>")
        if body_end < 0:
            raise ValueError(f"Cannot inject GoatCounter snippet into {path}: </body> not found")
        text = text[:body_end] + "  " + snippet + "\n" + text[body_end:]
    if text.count(f'data-goatcounter="{GOATCOUNTER_URL}"') != 1:
        raise ValueError(f"GoatCounter synchronization failed for {path}")
    path.write_text(text, encoding="utf-8", newline="\n")


def read_jsonld(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.index(JSONLD_START) + len(JSONLD_START)
    end = text.index(JSONLD_END, start)
    match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', text[start:end], re.S)
    if not match:
        raise ValueError(f"JSON-LD script is missing between sentinels in {path}")
    return json.loads(match.group(1))


def check_outputs(cards: list[ReportCard]) -> None:
    for path in (INDEX, CV, ROOT / "404.html"):
        if path.read_text(encoding="utf-8").count(f'data-goatcounter="{GOATCOUNTER_URL}"') != 1:
            raise ValueError(f"Expected exactly one configured GoatCounter snippet in {path}")

    atom_root = ET.parse(FEED).getroot()
    atom_entries = atom_root.findall(f"{{{ATOM_NS}}}entry")
    if len(atom_entries) != len(cards):
        raise ValueError(f"Atom entry count {len(atom_entries)} does not match card count {len(cards)}")
    for entry, card in zip(atom_entries, cards):
        if entry.findtext(f"{{{ATOM_NS}}}title") != card.title:
            raise ValueError(f"Atom title does not match report card: {card.title}")
        expected_fields = {
            "summary": card.summary,
            "published": rfc3339(card.published),
            "updated": rfc3339(card.updated),
        }
        for field, expected in expected_fields.items():
            if entry.findtext(f"{{{ATOM_NS}}}{field}") != expected:
                raise ValueError(f"Atom {field} does not match report card: {card.title}")
        link = entry.find(f"{{{ATOM_NS}}}link")
        if link is None or link.get("href") != card.url:
            raise ValueError(f"Atom link does not match report card: {card.title}")

    sitemap_root = ET.parse(SITEMAP).getroot()
    locations = [element.text for element in sitemap_root.findall(f"{{{SITEMAP_NS}}}url/{{{SITEMAP_NS}}}loc")]
    expected_locations = [SITE_URL, SITE_URL + "cv/"] + [card.url for card in cards]
    if locations != expected_locations:
        raise ValueError("Sitemap locations do not match the portfolio URLs and report cards")

    index_data = read_jsonld(INDEX)
    graph = index_data.get("@graph", [])
    types = {item.get("@type") for item in graph}
    if types != {"Person", "ItemList"}:
        raise ValueError(f"Portfolio JSON-LD has unexpected graph types: {types}")
    item_list = next(item for item in graph if item.get("@type") == "ItemList")
    if item_list.get("numberOfItems") != len(cards) or len(item_list.get("itemListElement", [])) != len(cards):
        raise ValueError("Portfolio ItemList does not match the report-card count")
    cv_data = read_jsonld(CV)
    if cv_data.get("@type") != "Person" or cv_data.get("@id") != SITE_URL + "#person":
        raise ValueError("CV JSON-LD does not describe the portfolio Person")


def check_drift(cards: list[ReportCard]) -> None:
    scratch_card = """<article class="report-card" data-published="2026-11-14" data-updated="2026-11-14" data-report-url="https://aloysius109.github.io/scratch-report/">
      <a class="card-link" href="https://aloysius109.github.io/scratch-report/summary/" aria-label="Quick read: Scratch report"></a>
      <h3 class="report-title">Scratch report</h3>
      <p class="report-description">A temporary parser check.</p>
      <span class="tag">Test</span>
    </article>"""
    scratch_cards = parse_cards(INDEX.read_text(encoding="utf-8") + scratch_card)
    if len(scratch_cards) != len(cards) + 1 or scratch_cards[-1].title != "Scratch report":
        raise ValueError("Drift self-check did not discover a scratch report card")
    scratch_feed = ET.fromstring(xml_bytes(atom_document(scratch_cards)))
    scratch_entries = scratch_feed.findall(f"{{{ATOM_NS}}}entry")
    scratch_sitemap = ET.fromstring(xml_bytes(sitemap_document(scratch_cards)))
    scratch_locations = scratch_sitemap.findall(f"{{{SITEMAP_NS}}}url")
    scratch_jsonld = index_jsonld(scratch_cards)
    scratch_list = next(item for item in scratch_jsonld["@graph"] if item["@type"] == "ItemList")
    scratch_item = scratch_list["itemListElement"][-1]["item"]
    if len(scratch_entries) != len(scratch_cards) or len(scratch_locations) != len(scratch_cards) + 2:
        raise ValueError("Drift self-check did not propagate the scratch card to XML outputs")
    if (
        scratch_list["numberOfItems"] != len(scratch_cards)
        or scratch_item["name"] != "Scratch report"
        or scratch_item["url"] != "https://aloysius109.github.io/scratch-report/"
    ):
        raise ValueError("Drift self-check did not propagate the scratch card to JSON-LD")


def main() -> None:
    cards = read_cards(INDEX)
    for path in (INDEX, CV, ROOT / "404.html"):
        inject_analytics(path)
    write_atom(cards, FEED)
    write_sitemap(cards, SITEMAP)
    inject_jsonld(INDEX, index_jsonld(cards))
    inject_jsonld(CV, person_jsonld())
    check_outputs(cards)
    check_drift(cards)
    print(f"Built and validated Atom feed, sitemap, and JSON-LD for {len(cards)} report cards; drift self-check passed.")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Refresh the local snapshot from Fourways Mall's public store directory."""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import json

SOURCE = "https://fourwaysmall.com/store-directory-all.php"
OUTPUT = Path(__file__).resolve().parents[1] / "mall-data.js"


class StoreParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.card = None
        self.paragraph = None
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            if self.card is None and "store-wrap" in attrs.get("class", "").split():
                self.card = {"paragraphs": [], "phone": "", "url": ""}
                self.depth = 1
            elif self.card is not None:
                self.depth += 1
        elif self.card is not None and tag == "p":
            self.paragraph = []
        elif self.card is not None and tag == "a":
            href = attrs.get("href", "")
            if href.startswith("tel:"):
                self.card["phone"] = href[4:]
            elif href.startswith("/store/"):
                self.card["url"] = "https://fourwaysmall.com" + href

    def handle_data(self, data):
        if self.paragraph is not None:
            self.paragraph.append(data)

    def handle_endtag(self, tag):
        if self.card is None:
            return
        if tag == "p" and self.paragraph is not None:
            text = " ".join("".join(self.paragraph).split())
            self.card["paragraphs"].append(text)
            self.paragraph = None
        elif tag == "div":
            self.depth -= 1
            if self.depth == 0:
                paragraphs = self.card["paragraphs"]
                name = next((p for p in paragraphs if p and not p.lower().startswith("store:")), "")
                unit = next((p.split(":", 1)[1].strip() for p in paragraphs if p.lower().startswith("store:")), "")
                if name:
                    self.paragraphs.append({
                        "name": name,
                        "unit": unit,
                        "phone": self.card["phone"],
                        "url": self.card["url"] or SOURCE,
                    })
                self.card = None


def main():
    request = Request(SOURCE, headers={"User-Agent": "FourwaysMallGuideDirectorySync/1.0"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = StoreParser()
    parser.feed(html)
    if len(parser.paragraphs) < 250:
        raise SystemExit(f"Directory parser found only {len(parser.paragraphs)} stores; keeping the previous data.")
    payload = {
        "project": "Fourways Mall Smart Guide",
        "source": SOURCE,
        "lastChecked": datetime.now(timezone.utc).date().isoformat(),
        "stores": parser.paragraphs,
    }
    OUTPUT.write_text("window.mallData = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"Updated {len(parser.paragraphs)} entries from the official mall directory.")


if __name__ == "__main__":
    main()

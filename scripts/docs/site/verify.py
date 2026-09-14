"""Check generated SEO contracts and all local destinations before publishing."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

import yaml

ROOT = Path(__file__).resolve().parents[3]


class SitePage(HTMLParser):
    """Collect the rendered fields search engines and navigation depend on."""

    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.meta: dict[str, str] = {}
        self.canonicals: list[str] = []
        self.title = ""
        self.heading_count = 0
        self.unnamed_dialogs = 0
        self.structured: list[object] = []
        self.current_tag = ""
        self.json_text: str | None = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.current_tag = tag
        if identifier := attributes.get("id"):
            self.ids.add(identifier)
        if tag == "h1":
            self.heading_count += 1
        if attributes.get("role") in {"dialog", "alertdialog"}:
            if not (attributes.get("aria-label") or attributes.get("aria-labelledby")):
                self.unnamed_dialogs += 1
        if tag == "meta":
            self.meta[attributes.get("name") or attributes.get("property") or ""] = (
                attributes.get("content") or ""
            )
        if tag == "link" and attributes.get("rel") == "canonical":
            self.canonicals.append(attributes.get("href") or "")
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.json_text = ""
        for attribute in ("href", "src"):
            if target := attributes.get(attribute):
                self.links.append(target)

    def handle_data(self, data: str) -> None:
        if self.current_tag == "title":
            self.title += data
        if self.json_text is not None:
            self.json_text += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.json_text is not None:
            self.structured.append(json.loads(self.json_text))
            self.json_text = None
        self.current_tag = ""


def verify_site(site: Path, base_url: str) -> list[str]:
    """Reject missing SEO fields, accidental publication, and broken local navigation."""
    pages = {path: SitePage(path) for path in site.rglob("*.html")}
    errors: list[str] = []
    titles: set[str] = set()
    descriptions: set[str] = set()
    urls: set[str] = set()
    for path, page in pages.items():
        relative = path.relative_to(site).as_posix()
        if page.unnamed_dialogs:
            errors.append(f"{relative}: dialog has no accessible name")
        if relative == "404.html":
            if "noindex" not in page.meta.get("robots", ""):
                errors.append("404.html must carry noindex")
            continue
        url = urljoin(base_url, relative.removesuffix("index.html"))
        urls.add(url)
        if page.canonicals != [url]:
            errors.append(f"{relative}: expected exactly one canonical {url}")
        if not page.title.strip() or page.title in titles:
            errors.append(f"{relative}: missing or duplicate title")
        titles.add(page.title)
        description = page.meta.get("description", "")
        if not description.strip() or description in descriptions:
            errors.append(f"{relative}: missing or duplicate description")
        descriptions.add(description)
        if "noindex" in page.meta.get("robots", ""):
            errors.append(f"{relative}: public page is marked noindex")
        if page.heading_count != 1:
            errors.append(f"{relative}: expected one h1, found {page.heading_count}")
        for field in ("og:title", "og:description", "og:url", "og:image", "twitter:card"):
            if not page.meta.get(field):
                errors.append(f"{relative}: missing {field}")
        if page.meta.get("og:url") != url:
            errors.append(f"{relative}: social URL disagrees with canonical")
        if not page.structured:
            errors.append(f"{relative}: missing structured data")
        for target in [*page.links, page.meta.get("og:image", "")]:
            errors.extend(verify_destination(target, url, base_url, site, pages, relative))
    sitemap = ElementTree.parse(site / "sitemap.xml")
    listed = {node.text for node in sitemap.findall(".//{*}loc")}
    if sitemap.findall(".//{*}lastmod"):
        errors.append("Sitemap must not use build timestamps as content modification dates")
    if listed != urls:
        errors.append(f"Sitemap mismatch: missing {urls - listed}; unexpected {listed - urls}")
    for forbidden in ("docs-internal", "console", "src", ".git", "AGENTS.md"):
        if (site / forbidden).exists():
            errors.append(f"Unexpected public source: {forbidden}")
    if not pages:
        errors.append("No HTML pages generated")
    return errors


def verify_destination(
    target: str,
    page_url: str,
    base_url: str,
    site: Path,
    pages: dict[Path, SitePage],
    source: str,
) -> list[str]:
    """Resolve links with browser URL rules, including deployment under a subpath."""
    absolute = urljoin(page_url, target)
    parsed = urlsplit(absolute)
    if not absolute.startswith(base_url):
        return []
    relative = unquote(parsed.path.removeprefix(urlsplit(base_url).path))
    destination = site / relative
    if destination.is_dir():
        destination /= "index.html"
    if not destination.is_file():
        return [f"{source}: missing local target {target}"]
    if parsed.fragment and destination in pages:
        if unquote(parsed.fragment) not in pages[destination].ids:
            return [f"{source}: missing fragment {target}"]
    return []


def main() -> int:
    """Verify the configured site, or an explicit built output directory."""
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    site = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / config["site_dir"]
    errors = verify_site(site, config["site_url"])
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Verified {len(list(site.rglob('*.html'))) - 1} public pages and their local links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

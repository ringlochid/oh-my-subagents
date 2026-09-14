"""Adapt maintained repository sources to the public static website."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from scripts.docs.markdown_links import (
    MARKDOWN_LINK_PATTERN,
    iter_non_fenced_lines,
    normalize_link_target,
)

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "examples/workflows/README.md"
CATALOG_URI = "starter-teams.md"


def on_files(files: Files, config: MkDocsConfig) -> Files:
    """Publish the catalog and original product mark without duplicating their sources."""
    files.append(File.generated(config, CATALOG_URI, abs_src_path=str(CATALOG)))
    files.append(
        File.generated(
            config,
            "assets/oms-mark.svg",
            abs_src_path=str(ROOT / "console/public/assets/oms-mark.svg"),
        )
    )
    return files


def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
    """Keep repo-relative source links usable on the rendered site."""
    source = CATALOG if page.file.src_uri == CATALOG_URI else ROOT / "docs" / page.file.src_uri
    if source == CATALOG:
        page.meta.update(
            title="Starter AI teams: coding, research, recovery, and review",
            description=(
                "Choose an OMS Starter team for feature delivery, incident recovery, research, "
                "migration, experiments, or security. Compare missions and responsibilities."
            ),
        )
        page.edit_url = f"{config.repo_url}/edit/main/examples/workflows/README.md"
    lines = markdown.splitlines(keepends=True)
    for line_number, line in iter_non_fenced_lines(markdown):
        ending = "\n" if lines[line_number - 1].endswith("\n") else ""
        lines[line_number - 1] = (
            MARKDOWN_LINK_PATTERN.sub(
                lambda match: rewrite_link(match, source, page.file.src_uri, config), line
            )
            + ending
        )
    return "".join(lines)


def rewrite_link(match: re.Match[str], source: Path, source_uri: str, config: MkDocsConfig) -> str:
    """Route published documents locally and other repository sources to GitHub."""
    target = normalize_link_target(match.group("target"))
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return match.group(0)
    destination = (source.parent / parsed.path).resolve()
    if not destination.is_relative_to(ROOT):
        raise ValueError(f"Documentation link escapes the repository: {source}: {target}")
    suffix = f"#{parsed.fragment}" if parsed.fragment else ""
    if destination == CATALOG:
        site_uri = CATALOG_URI
    elif destination.is_relative_to(ROOT / "docs"):
        site_uri = destination.relative_to(ROOT / "docs").as_posix()
    else:
        kind = "tree" if destination.is_dir() else "blob"
        repository_path = quote(destination.relative_to(ROOT).as_posix())
        replacement = f"{config.repo_url}/{kind}/main/{repository_path}"
        return replace_link_target(match, target, replacement + suffix)
    replacement = Path(os.path.relpath(site_uri, Path(source_uri).parent)).as_posix()
    return replace_link_target(match, target, replacement + suffix)


def replace_link_target(match: re.Match[str], target: str, replacement: str) -> str:
    """Replace the destination without changing a label that contains the same filename."""
    offset = match.start("target") - match.start()
    return match.group(0)[:offset] + match.group(0)[offset:].replace(target, replacement, 1)


def on_page_context(
    context: dict[str, object], page: Page, config: MkDocsConfig, nav: object
) -> None:
    """Describe visible pages without fabricated rich-result claims."""
    title = page.meta.get("title") or page.title
    page.meta["structured_data"] = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite" if page.is_homepage else "TechArticle",
                "@id": page.canonical_url,
                "url": page.canonical_url,
                "name": title,
                "description": page.meta.get("description"),
                "inLanguage": "en",
            },
            *(
                [
                    {
                        "@type": "BreadcrumbList",
                        "itemListElement": [
                            {
                                "@type": "ListItem",
                                "position": 1,
                                "name": config.site_name,
                                "item": config.site_url,
                            },
                            {
                                "@type": "ListItem",
                                "position": 2,
                                "name": title,
                                "item": page.canonical_url,
                            },
                        ],
                    }
                ]
                if not page.is_homepage
                else []
            ),
        ],
    }


def on_post_page(output: str, page: Page, config: MkDocsConfig) -> str:
    """Name the search dialog in rendered Markdown pages."""
    return name_search_dialog(output)


def on_post_template(output: str, template_name: str, config: MkDocsConfig) -> str:
    """Apply the same accessible name to standalone templates such as the 404 page."""
    return name_search_dialog(output)


def name_search_dialog(output: str) -> str:
    """Name Material 9.7's search dialog without copying its complete theme template."""
    return output.replace(
        'data-md-component="search" role="dialog"',
        'data-md-component="search" role="dialog" aria-label="Site search"',
    )

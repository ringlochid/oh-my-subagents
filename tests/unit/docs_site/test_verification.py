"""Failure-oriented checks for the public website's generated-output gate."""

from pathlib import Path

from scripts.docs.site.verify import SitePage, verify_destination, verify_site

BASE_URL = "https://example.com/project/"


def write_minimal_site(root: Path) -> Path:
    (root / "index.html").write_text(
        "<html><head><title>Project overview</title>"
        '<link rel="canonical" href="https://example.com/project/">'
        '<meta name="description" content="A useful project overview">'
        '<meta property="og:title" content="Project overview">'
        '<meta property="og:description" content="A useful project overview">'
        '<meta property="og:url" content="https://example.com/project/">'
        '<meta property="og:image" content="https://example.com/project/preview.png">'
        '<meta name="twitter:card" content="summary_large_image">'
        '<script type="application/ld+json">{"@type":"WebSite"}</script>'
        '</head><body><h1 id="overview">Project overview</h1>'
        '<a href="#overview">Overview</a></body></html>',
        encoding="utf-8",
    )
    (root / "404.html").write_text('<meta name="robots" content="noindex">', encoding="utf-8")
    (root / "preview.png").write_bytes(b"image fixture")
    (root / "sitemap.xml").write_text(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        "<url><loc>https://example.com/project/</loc></url></urlset>",
        encoding="utf-8",
    )
    return root


def test_accepts_complete_public_site(tmp_path: Path) -> None:
    assert verify_site(write_minimal_site(tmp_path), BASE_URL) == []


def test_rejects_missing_social_image(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    (site / "preview.png").unlink()
    assert any("missing local target" in error for error in verify_site(site, BASE_URL))


def test_rejects_noindex_on_public_page(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    page = site / "index.html"
    page.write_text(
        page.read_text(encoding="utf-8") + '<meta name="robots" content="noindex">',
        encoding="utf-8",
    )
    assert any("marked noindex" in error for error in verify_site(site, BASE_URL))


def test_rejects_wrong_deployment_prefix_and_sitemap(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    errors = verify_site(site, "https://example.com/another-project/")
    assert any("canonical" in error for error in errors)
    assert any("Sitemap mismatch" in error for error in errors)


def test_rejects_broken_fragments_and_checks_absolute_local_links(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    pages = {site / "index.html": SitePage(site / "index.html")}
    assert verify_destination(
        BASE_URL + "#missing", BASE_URL, BASE_URL, site, pages, "index.html"
    ) == ["index.html: missing fragment https://example.com/project/#missing"]
    assert not verify_destination(
        "https://github.com/example/project", BASE_URL, BASE_URL, site, pages, "index.html"
    )


def test_rejects_internal_tree_in_public_output(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    (site / "docs-internal").mkdir()
    assert "Unexpected public source: docs-internal" in verify_site(site, BASE_URL)


def test_rejects_an_unnamed_search_dialog(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    page = site / "index.html"
    page.write_text(
        page.read_text(encoding="utf-8") + '<div role="dialog">Search</div>',
        encoding="utf-8",
    )
    assert any("accessible name" in error for error in verify_site(site, BASE_URL))


def test_rejects_synthetic_sitemap_dates(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    sitemap = site / "sitemap.xml"
    sitemap.write_text(
        sitemap.read_text(encoding="utf-8").replace(
            "</url>", "<lastmod>2026-09-14</lastmod></url>"
        ),
        encoding="utf-8",
    )
    assert any("build timestamps" in error for error in verify_site(site, BASE_URL))


def test_error_page_also_requires_a_named_dialog(tmp_path: Path) -> None:
    site = write_minimal_site(tmp_path)
    (site / "404.html").write_text(
        '<meta name="robots" content="noindex"><div role="dialog">Search</div>',
        encoding="utf-8",
    )
    assert "404.html: dialog has no accessible name" in verify_site(site, BASE_URL)

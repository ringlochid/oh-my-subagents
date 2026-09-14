# Public documentation publishing

Status: Reference

This page owns the public documentation website, its generated delivery, search metadata, and publication checks. Product behavior remains owned by the subject pages routed from the [internal documentation](../README.md).

## Sources and output

`docs/**` is the maintained public documentation source. `examples/workflows/README.md` remains the Starter catalog owner and is included in the site at build time. MkDocs Material renders these sources as static HTML; it does not publish internal canon, credentials, runtime data, or the interactive Console.

`mkdocs.yml` owns navigation, the canonical site URL, and theme configuration. `scripts/docs/site/**` owns build hooks, templates, the pinned documentation dependencies, and generated-page verification. The build writes only under ignored `build/`. Source links outside the published documentation resolve to their actual GitHub files. The website does not create a second editable copy of any maintained document.

The build uses MkDocs 1.6.1 and Material 9.7.7, with transitive dependencies pinned and hashed. Material's published compatibility notice identifies a breaking MkDocs 2 transition. Do not upgrade the generator across that boundary without checking hooks, theme overrides, output contracts, and browser proof. The generator is build-time tooling; production serves static files.

The canonical production address is `https://ringlochid.me/oh-my-subagents/`. GitHub Pages inherits `ringlochid.me` from the account's user site. This project does not change the user site's domain, DNS, content, or root robots policy.

## Search and presentation contract

Every indexable page has one descriptive title, one main heading, an individual description, a canonical URL, and social metadata. Navigation and body links are ordinary HTML anchors. The sitemap contains only canonical public pages. The error page is excluded from indexing and the sitemap. On-site search operates in the browser without a tracking service.

The sitemap omits `lastmod` because build and checkout timestamps do not establish when content substantively changed. Add modification dates only through a source that preserves actual content history. Body links remain distinguishable without color, and the search dialog has an accessible name.

Structured data describes only visible, supported content. Never invent reviews, ratings, pricing, benchmark results, or claims about automatic recovery. Existing product illustrations remain authentic. Website styling is independent of n8n-derived Console styles and stays within the repository's MIT boundary.

Tutorials must cite supported setup and runtime behavior, distinguish sample missions from observed runs, and include a checked-outcome step. Search terminology may explain familiar equivalents but must not redefine Workflow, Task, Checkpoint, or Result. Each substantive documentation edit should update its description when its purpose changes.

## Build and proof

Install the pinned website requirements with `make docs-site-install`, build with `make docs-site-build`, and run `make docs-site-check`. The check builds in strict mode and verifies the generated HTML, local links and fragments, canonical URLs, descriptions, sitemap coverage, social metadata, structured data, and publication exclusions.

Run `make check-docs` as well as the website gate for maintained documentation changes. Browser proof covers desktop and narrow layouts, navigation, search, code copying, and keyboard access. A generated site must remain readable with JavaScript disabled.

The documentation workflow builds and verifies pull requests without deployment credentials. Main-branch pushes and explicit dispatches may deploy the verified artifact through the GitHub Pages environment. Publication must be followed by a live check of the homepage, representative guides, asset URLs, sitemap, canonical metadata, and an unknown URL's HTTP 404 response.

## Measurement and discovery

Search Console ownership verification and sitemap submission use the owner's authenticated account. A URL-prefix property may cover this project path without changing the domain's DNS. A successful sitemap submission proves receipt, not indexing or ranking. Record actual index coverage, search queries, impressions, and clicks when available; never substitute a search-result sample for those metrics.

The project sitemap can be submitted directly to Search Console. A `robots.txt` inside this project path does not control crawling: robots policy is read at the origin root. Do not imply that publishing a project-level robots file changes the root policy.

GitHub's description and homepage should identify the product and link to the canonical site. Package metadata changes apply to a future package release; updating the repository does not rewrite an already-published PyPI release. Do not publish a software release solely to refresh SEO copy without release authorization and package verification.

## Research basis

- [Google SEO fundamentals](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) informs crawlable navigation, clear titles, descriptions, and useful content.
- [Helpful content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) informs task-focused tutorials and evidence boundaries.
- [Canonical URL guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) informs canonical links and sitemap consistency.
- [AI search features](https://developers.google.com/search/docs/appearance/ai-features) confirms that ordinary SEO practices remain applicable; no special AI text file or schema is required.
- [GitHub Pages custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages) owns inherited project-domain behavior.
- [GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) owns artifact deployment and environment permissions.
- [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/) and [Material setup](https://squidfunk.github.io/mkdocs-material/creating-your-site/) own static rendering and theme configuration.

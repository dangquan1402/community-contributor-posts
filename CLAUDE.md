# Community Contributor Posts

A collection of LinkedIn posts discussing lessons learned from building LLM-powered applications.

## Structure

Each post has 3 versions:
- `NNN-<slug>.md` — full version (renders on GitHub with mermaid support)
- `NNN-linkedin-version.md` — short version for LinkedIn (under 3,000 chars)
- `_posts/YYYY-MM-DD-<slug>.md` — Jekyll version for GitHub Pages (uses `<pre class="mermaid">` for diagrams)

## Conventions

- Write in a conversational, first-person tone — not a blog-style markdown article
- Minimal markdown formatting in full/LinkedIn versions — no headers, bullet lists, or bold text
- Tables and mermaid diagrams are encouraged for visual comparison
- Always include reference links at the bottom of the full version
- Jekyll posts use `<pre class="mermaid">` tags (not code blocks) for diagram rendering
- Full posts use ` ```mermaid ` code blocks (GitHub renders these natively)
- Each post should end with a discussion question
- LinkedIn version should link to the full version on GitHub

## GitHub Pages

- Theme: minima
- Mermaid support: loaded via CDN in `_includes/mermaid.html`, included in `_layouts/post.html`
- URL: https://dangquan1402.github.io/community-contributor-posts/

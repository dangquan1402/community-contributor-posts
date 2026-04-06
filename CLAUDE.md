# LLM Engineering Notes

Practical notes on building LLM-powered applications — shared on LinkedIn and X/Twitter.

## Structure

Each post lives in `posts/NNN-<slug>/` with 3 platform versions, plus a Jekyll version:

```
posts/NNN-<slug>/
  post.md          — full version (renders on GitHub with mermaid support)
  linkedin.md      — short version for LinkedIn (under 3,000 chars)
  x-thread.md      — X/Twitter thread (4-8 tweets, 280 chars each)

_posts/YYYY-MM-DD-<slug>.md  — Jekyll version for GitHub Pages
```

## Writing Conventions

- Write in a conversational, first-person tone — not a blog-style markdown article
- Full/LinkedIn versions: minimal markdown — no headers, bullet lists, or bold text
- Jekyll posts (_posts/): use `## Section Headers` and kramdown TOC (see below)
- Tables and mermaid diagrams are encouraged for visual comparison
- Always include a numbered references section at the bottom (see References format below)
- Use inline references in body text: `[text [N]](url)` linking to the numbered refs
- Include code snippets (pseudo-code or real) where they clarify a concept
- Each reference line must end with two trailing spaces for markdown line breaks
- Each post should end with a discussion question
- LinkedIn version should link to the full post on GitHub Pages (not the GitHub repo)
  - URL pattern: `https://dangquan1402.github.io/llm-engineering-notes/YYYY/MM/DD/<slug>.html`

## Jekyll Post Structure

Jekyll posts use section headers and an auto-generated TOC. Structure:

```
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
---

Introduction paragraph (1-2 sentences setting context).

* TOC
{:toc}

## First Section

Content...

## Second Section

Content...

---

References:

[1] ...  
[2] ...  
```

The TOC goes after the introduction paragraph, before the first `##` heading.

## References Format

Inspired by [Lilian Weng's blog](https://lilianweng.github.io/). Use numbered references at the bottom of full posts and Jekyll posts:

```
References:

[1] Author et al. ["Paper Title."](https://arxiv.org/abs/XXXX.XXXXX) Venue Year.
[2] Author et al. ["Paper Title."](https://link) Venue Year.
[3] ["Documentation Page Title."](https://docs.example.com/page) Provider.
```

In-body text, use inline author-date citations linked directly:
```
The [Prometheus paper (Kim et al., ICLR 2024)](https://arxiv.org/abs/2310.08491) showed that...
```

For LinkedIn versions, references are not needed — link to the full post on GitHub Pages instead.

## X/Twitter Thread Format

Each post gets an X thread version (`NNN-x-thread.md`):
- 4-8 tweets, each under 280 characters
- Tweet 1: hook — why should I care
- Tweets 2-6: one key insight per tweet, concrete numbers/examples
- Last tweet: CTA link to GitHub Pages + 2-3 hashtags
- Format: `1/N` numbering at the start of each tweet
- Keep it conversational, use line breaks, no walls of text
- Arrows (`→`) for bullet points within tweets

## Code Snippets

Use fenced code blocks with language tags for pseudo-code or real examples:
- `python` for Python snippets
- `json` for API request/response examples
- `text` or no tag for pseudo-code

Keep snippets short and focused — illustrate one concept per snippet. Pseudo-code is preferred over full implementations.

## Mermaid Diagrams & Visual Guidelines

Use `/mermaid-review` to review and improve diagrams in a post.

### Rendering targets

- Full posts (.md): fenced ` ```mermaid ` code blocks (GitHub renders natively)
- Jekyll posts (_posts/): `<pre class="mermaid">` HTML tags

### When to use a diagram vs a table

**Use a table when:**
- Comparing things (A vs B, before/after, provider differences)
- Items have multiple attributes (table rows handle this; graph nodes don't)
- Labels would be long/cramped in a diagram
- Showing two disconnected paths side by side (e.g., "bad" vs "good")
- Showing concrete numbers or calculations

**Use a diagram when:**
- Showing a flow with a feedback loop or cycle
- Showing a pipeline with clear directionality (A → B → C)
- The visual shape itself communicates meaning (gradient, hierarchy)

**Often the best approach is both:** a compact diagram for the shape + a table for the details.

### Diagram type selection

- `timeline` — chronological progressions (feature launches, adoption phases). Use `section` to group.
- `graph LR` — preferred for flows, pipelines, priority chains, cycles. Reads left-to-right.
- `graph TD` — avoid in most cases. Only for deep decision trees with 4+ branching levels.

### Do NOT use `graph LR` for timelines. Use `timeline` instead.

### Graph diagram rules

- **Labels: 1-3 words per node.** Put details in surrounding text or a companion table.
- Color palette:
  - Green: `fill:#2a9d8f`, `fill:#2d6a4f`, `fill:#40916c` (positive/final states)
  - Red/orange: `fill:#e76f51`, `fill:#f4a261` (problem/initial states)
  - Yellow: `fill:#e9c46a` (decisions/intermediate)
  - Dark: `fill:#264653` (neutral/start)
  - Green gradients (dark→light) for stability/priority spectrums

## LinkedIn Carousels

PDF carousels for LinkedIn posts are generated from `carousels/` directory:
- `carousel_base.py` — reusable base class (white background, teal accents, tables, bullets, stat boxes)
- `NNN_slug.py` — per-post slide definitions + mermaid rendering
- `output/` — generated PDFs (gitignored)
- Run: `cd carousels && python3 NNN_slug.py`
- Specs: 1080×1080 square, 6-9 slides, PDF under 3 MB
- CTA slide links to GitHub Pages URL (not GitHub repo)

## GitHub Pages

- Theme: minima
- Mermaid support: loaded via CDN in `_includes/mermaid.html`, included in `_layouts/post.html`
- URL: https://dangquan1402.github.io/llm-engineering-notes/
- Post URL pattern: `https://dangquan1402.github.io/llm-engineering-notes/YYYY/MM/DD/<slug>.html`

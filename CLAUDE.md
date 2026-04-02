# Community Contributor Posts

A collection of LinkedIn posts discussing lessons learned from building LLM-powered applications.

## Structure

Each post has 3 versions:
- `NNN-<slug>.md` — full version (renders on GitHub with mermaid support)
- `NNN-linkedin-version.md` — short version for LinkedIn (under 3,000 chars)
- `_posts/YYYY-MM-DD-<slug>.md` — Jekyll version for GitHub Pages (uses `<pre class="mermaid">` for diagrams)

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
- LinkedIn version should link to the full version on GitHub

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

For LinkedIn versions, references are not needed — link to the full version instead.

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

## GitHub Pages

- Theme: minima
- Mermaid support: loaded via CDN in `_includes/mermaid.html`, included in `_layouts/post.html`
- URL: https://dangquan1402.github.io/community-contributor-posts/

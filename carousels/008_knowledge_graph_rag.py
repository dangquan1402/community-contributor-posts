#!/usr/bin/env python3
"""Generate LinkedIn carousel for Post 008 — Knowledge Graph RAG."""

import os
import subprocess
import tempfile
from carousel_base import CarouselPDF, TEXT, CONTENT_W

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def render_mermaid(mmd_content, output_path):
    """Render mermaid diagram to PNG via mermaid-cli."""
    with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w", delete=False) as f:
        f.write(mmd_content)
        mmd_path = f.name
    try:
        subprocess.run(
            ["npx", "-y", "@mermaid-js/mermaid-cli", "-i", mmd_path, "-o", output_path,
             "-w", "1000", "-b", "transparent"],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(mmd_path)


# ── Render diagrams ──
kg_example_png = os.path.join(OUTPUT_DIR, "008-kg-example.png")
pipeline_png = os.path.join(OUTPUT_DIR, "008-pipeline.png")
update_png = os.path.join(OUTPUT_DIR, "008-update-cost.png")
code_kg_png = os.path.join(OUTPUT_DIR, "008-code-kg.png")

render_mermaid("""graph LR
    E["Einstein"] -->|bornIn| U["Ulm"]
    E -->|field| P["Physics"]
    E -->|won| NP["Nobel 1921"]
    NP -->|category| P
    U -->|country| DE["Germany"]

    style E fill:#264653,stroke:#264653,color:#fff
    style U fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style P fill:#e9c46a,stroke:#e9c46a,color:#000
    style NP fill:#f4a261,stroke:#f4a261,color:#000
    style DE fill:#2d6a4f,stroke:#2d6a4f,color:#fff
""", kg_example_png)

render_mermaid("""graph LR
    DOC["Documents"] --> CHUNK["Chunk"]
    CHUNK --> EXT["Extract\nEntities"]
    EXT --> KG["Knowledge\nGraph"]
    KG --> COM["Detect\nCommunities"]
    COM --> SUM["Summarize"]
    SUM --> QA["Map-Reduce\nQA"]

    style DOC fill:#264653,stroke:#264653,color:#fff
    style CHUNK fill:#e76f51,stroke:#e76f51,color:#fff
    style EXT fill:#f4a261,stroke:#f4a261,color:#000
    style KG fill:#e9c46a,stroke:#e9c46a,color:#000
    style COM fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style SUM fill:#40916c,stroke:#40916c,color:#fff
    style QA fill:#2d6a4f,stroke:#2d6a4f,color:#fff
""", pipeline_png)

render_mermaid("""graph LR
    NEW["New Docs"] --> EXT["Re-extract"]
    EXT --> RES["Resolve vs\nExisting"]
    RES --> DEDUP["Dedup\n(full graph)"]
    DEDUP --> RECOM["Re-detect\nCommunities"]
    RECOM --> RESUM["Re-summarize\n(cascade)"]

    style NEW fill:#e76f51,stroke:#e76f51,color:#fff
    style EXT fill:#f4a261,stroke:#f4a261,color:#000
    style RES fill:#e9c46a,stroke:#e9c46a,color:#000
    style DEDUP fill:#f4a261,stroke:#f4a261,color:#000
    style RECOM fill:#e76f51,stroke:#e76f51,color:#fff
    style RESUM fill:#e76f51,stroke:#e76f51,color:#fff
""", update_png)

render_mermaid("""graph LR
    CODE["Source Code"] --> AST["AST"]
    CODE --> LSP["LSP"]
    CODE --> DEP["Dep Graph"]
    CODE --> SA["CodeQL"]
    KG["LLM-Extracted\nCode KG"]

    AST -->|"free, lossless"| R["Same\nRelations"]
    LSP -->|"free, real-time"| R
    DEP -->|"free, exact"| R
    SA -->|"free, precise"| R
    KG -->|"$$$, lossy"| R

    style CODE fill:#264653,stroke:#264653,color:#fff
    style AST fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style LSP fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style DEP fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style SA fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style KG fill:#e76f51,stroke:#e76f51,color:#fff
    style R fill:#e9c46a,stroke:#e9c46a,color:#000
""", code_kg_png)

print("Diagrams rendered.")

# ── Build carousel ──
pdf = CarouselPDF()

# Slide 1: Hook
pdf.slide_start()
y = 200
y = pdf.tag(y, "Knowledge Graph RAG")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Structured Retrieval\nIs Powerful — But the\nMaintenance Cost Is Real")
y += 40
y = pdf.body_text(y, "GraphRAG wins on comprehensiveness.\nBut what happens when your data changes?", size=34)
pdf.footer_text("Dquan's LLM Notes  |  008")

# Slide 2: What is a Knowledge Graph
pdf.slide_start()
y = 100
y = pdf.tag(y, "The Basics")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Knowledge Graphs 101", size=46)
y += 15
y = pdf.add_image_centered(y, kg_example_png, max_h=250)
y += 10
y = pdf.body_text(y, "Nodes = entities, edges = relations.\nExplicit, traversable, multi-hop reasoning.\nWikidata alone has 100B+ triples.", size=30)
pdf.footer_text()

# Slide 3: GraphRAG Pipeline
pdf.slide_start()
y = 100
y = pdf.tag(y, "GraphRAG Pipeline")
y = pdf.accent_line(y)
y = pdf.title_text(y, "From Documents to Answers", size=42)
y += 15
y = pdf.add_image_centered(y, pipeline_png, max_h=180)
y += 10
y = pdf.table(y,
    ["Step", "What", "Cost"],
    [
        ["Extract", "LLM reads every chunk", "~$30 / 2K articles"],
        ["Resolve", "Deduplicate entities", "Multi-step pipeline"],
        ["Detect", "Leiden communities", "Needs graph DB"],
        ["Summarize", "LLM per community", "1000s of LLM calls"],
    ],
    col_widths=[200, 360, 360],
)
pdf.footer_text()

# Slide 4: GraphRAG vs Vector RAG
pdf.slide_start()
y = 120
y = pdf.tag(y, "Benchmarks")
y = pdf.accent_line(y)
y = pdf.title_text(y, "GraphRAG vs Vector RAG", size=46)
y += 20
y = pdf.table(y,
    ["Metric", "Winner", "Win Rate"],
    [
        ["Comprehensiveness", "GraphRAG", "72-83%"],
        ["Diversity", "GraphRAG", "62-82%"],
        ["Directness", "Vector RAG", "Wins"],
        ["Empowerment", "Mixed", "Depends"],
    ],
    col_widths=[340, 300, 280],
)
y += 30
y = pdf.body_text(y, "Vector RAG finds the needle.\nGraphRAG describes the haystack.", size=32, color=TEXT)
pdf.footer_text()

# Slide 5: The Maintenance Problem
pdf.slide_start()
y = 100
y = pdf.tag(y, "The Hidden Cost")
y = pdf.accent_line(y)
y = pdf.title_text(y, "What Happens When\nYour Knowledge Changes?", size=44)
y += 15
y = pdf.add_image_centered(y, update_png, max_h=180)
y += 10
y = pdf.bullet(y, "New entities must resolve against full graph", size=28)
y += 5
y = pdf.bullet(y, "Dedup gets harder as graph grows (100K+)", size=28)
y += 5
y = pdf.bullet(y, "Community structure shifts → stale summaries", size=28)
y += 5
y = pdf.bullet(y, "Bottom-up summarization cascades on changes", size=28)
pdf.footer_text()

# Slide 6: Code KGs — Already Solved
pdf.slide_start()
y = 100
y = pdf.tag(y, "Code Knowledge Graphs")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Code Already Has Structure", size=44)
y += 15
y = pdf.add_image_centered(y, code_kg_png, max_h=200)
y += 10
y = pdf.table(y,
    ["Tool", "Provides", "Cost"],
    [
        ["AST (tree-sitter)", "Full syntax structure", "Zero"],
        ["LSP", "Defs, refs, call hierarchy", "Zero"],
        ["Package mgrs", "Dependency graphs", "Zero"],
        ["CodeQL", "Data flow, taint tracking", "Near-zero"],
    ],
    col_widths=[300, 360, 260],
)
pdf.footer_text()

# Slide 7: When to Use What
pdf.slide_start()
y = 100
y = pdf.tag(y, "Decision Guide")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Which RAG Approach?", size=44)
y += 20
y = pdf.table(y,
    ["Scenario", "Use"],
    [
        ["Static KB, global queries", "GraphRAG"],
        ["Rapidly changing docs", "Vector RAG"],
        ["Specific factual lookups", "Vector RAG"],
        ["Existing curated KG", "KG-augmented RAG"],
        ["Mixed query types", "Hybrid"],
    ],
    col_widths=[540, 380],
)
y += 30
y = pdf.body_text(y, "GraphRAG shines on static corpora with\nglobal, thematic questions.", size=30, color=TEXT)
pdf.footer_text()

# Slide 8: Key Takeaway
pdf.slide_start()
y = 150
y = pdf.tag(y, "The Bottom Line")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Structured data is\nharder to update than\nunstructured data", size=48)
y += 40
y = pdf.body_text(y, "Vector RAG: add a doc = chunk, embed, append.\nGraphRAG: add a doc = potentially restructure\nyour entire knowledge representation.", size=30)
y += 30
y = pdf.body_text(y, "The future is incremental graph updates.\nUntil then, choose based on how often\nyour knowledge changes.", size=30, color=TEXT)
pdf.footer_text()

# Slide 9: CTA
pdf.slide_start()
y = 250
y = pdf.title_text(y, "Full post with diagrams,\ncode examples, and references", size=44)
y += 30
y = pdf.accent_line(y, width=CONTENT_W)
y += 20
y = pdf.link_text(y, "dangquan1402.github.io/llm-engineering-notes",
    "https://dangquan1402.github.io/llm-engineering-notes/2026/04/03/knowledge-graph-rag.html")
y += 40
y = pdf.body_text(y, "Are you using knowledge graphs in production?\nBuilding from scratch or leveraging existing ones?", size=30)
pdf.footer_text("Dquan's LLM Notes  |  @quandang")

# ── Output ──
output_path = os.path.join(OUTPUT_DIR, "008-knowledge-graph-rag-carousel.pdf")
pdf.output(output_path)
print(f"Created: {output_path}")

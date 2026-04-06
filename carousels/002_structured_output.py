#!/usr/bin/env python3
"""Generate LinkedIn carousel for Post 002 — Structured Output Evolution."""

import os
import subprocess
import tempfile
from carousel_base import CarouselPDF, ORANGE, CONTENT_W

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
timeline_png = os.path.join(OUTPUT_DIR, "002-timeline.png")
flow_png = os.path.join(OUTPUT_DIR, "002-flow.png")

render_mermaid("""timeline
    title Structured Output Evolution
    section Hack Era
        Pre-2023 : Prompt Hacking
                 : "Return JSON" and pray
    section Function Calling
        Jun 2023 : OpenAI Function Calling
                 : JSON Schema for params
        Dec 2023 : Google Gemini
    section JSON Mode
        Nov 2023 : OpenAI JSON Mode
                 : Valid JSON, no schema
    section Structured Outputs
        Apr 2024 : Anthropic Tool Use
        Aug 2024 : OpenAI Strict Mode
                 : Guaranteed schema
""", timeline_png)

render_mermaid("""graph LR
    A["Pydantic Model"] --> B["JSON Schema"]
    B --> C["LLM"]
    C --> D{"Valid?"}
    D -->|Yes| E["Structured Data"]
    D -->|No| F["Retry + Error"]
    F --> C

    style A fill:#264653,stroke:#264653,color:#fff
    style E fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style F fill:#e76f51,stroke:#e76f51,color:#fff
    style D fill:#e9c46a,stroke:#e9c46a,color:#000
""", flow_png)

print("Diagrams rendered.")

# ── Build carousel ──
pdf = CarouselPDF()

# Slide 1: Hook
pdf.slide_start()
y = 200
y = pdf.tag(y, "Structured Output")
y = pdf.accent_line(y)
y = pdf.title_text(y, "How LLMs Learned\nto Speak JSON")
y += 40
y = pdf.body_text(y, "From 'please return JSON' and pray\nto guaranteed schema compliance.", size=34)
pdf.footer_text("Dquan's LLM Notes  |  002")

# Slide 2: The Problem
pdf.slide_start()
y = 120
y = pdf.tag(y, "The Hack Era")
y = pdf.accent_line(y)
y = pdf.title_text(y, "We used to beg\nthe model for JSON", size=46)
y += 20
y = pdf.body_text(y, '"You MUST respond in this exact JSON format..."\n\nSometimes it worked. Sometimes it added extra text.\nSometimes it hallucinated field names.\nWe had to parse, validate, retry. Fragile.', size=28)
y += 30
y = pdf.stat_box(y, "reliability of prompt-hacked JSON extraction", "~60-70%", color=ORANGE)
pdf.footer_text()

# Slide 3: Evolution Timeline
pdf.slide_start()
y = 80
y = pdf.tag(y, "The Evolution")
y = pdf.accent_line(y)
y = pdf.title_text(y, "4 Eras of Structured Output", size=42)
y += 15
y = pdf.add_image_centered(y, timeline_png, max_h=550)
pdf.footer_text()

# Slide 4: Feature Comparison
pdf.slide_start()
y = 100
y = pdf.tag(y, "Comparison")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Each Step Removed Uncertainty", size=42)
y += 20
y = pdf.table(y,
    ["", "Prompt Hack", "Func Call", "JSON Mode", "Strict Output"],
    [
        ["Valid JSON", "No", "Best-effort", "Yes", "Yes"],
        ["Schema", "No", "Best-effort", "No", "Guaranteed"],
        ["Reliability", "Low", "Medium", "Med-High", "Very High"],
        ["Date", "Pre-2023", "Jun 2023", "Nov 2023", "Aug 2024"],
    ],
    col_widths=[160, 170, 170, 170, 250],
)
pdf.footer_text()

# Slide 5: Provider Support
pdf.slide_start()
y = 100
y = pdf.tag(y, "Provider Support")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Everyone Converged", size=42)
y += 20
y = pdf.table(y,
    ["Provider", "Function Calling", "JSON Mode", "Strict Output"],
    [
        ["OpenAI", "Jun 2023", "Nov 2023", "Aug 2024"],
        ["Anthropic", "Apr 2024", "Forced tool use", "Forced tool use"],
        ["Google", "Dec 2023", "Late 2024", "response_schema"],
    ],
    col_widths=[200, 230, 230, 260],
)
y += 30
y = pdf.body_text(y, "The ecosystem recognized that structured output\nis essential for production LLM applications.", size=28)
pdf.footer_text()

# Slide 6: Pydantic Flow
pdf.slide_start()
y = 100
y = pdf.tag(y, "How It Works")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Pydantic as the Standard", size=42)
y += 20
y = pdf.add_image_centered(y, flow_png, max_h=200)
y += 10
y = pdf.table(y,
    ["Pydantic Feature", "JSON Schema", "LLM Uses It For"],
    [
        ['Field(description="...")', '"description": "..."', "Understanding context"],
        ['Literal["a", "b"]', '"enum": ["a", "b"]', "Forced choice"],
        ["Field(ge=0, le=1)", "min: 0, max: 1", "Constrained range"],
        ["Nested BaseModel", "Nested object", "Sub-structures"],
    ],
    col_widths=[300, 280, 340],
)
pdf.footer_text()

# Slide 7: Libraries
pdf.slide_start()
y = 120
y = pdf.tag(y, "Libraries")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Native SDK vs LangChain\nvs Instructor", size=42)
y += 20
y = pdf.table(y,
    ["Library", "Approach", "Trade-off"],
    [
        ["Native SDK", "Direct API", "Full control, provider lock-in"],
        ["LangChain", "Unified abstraction", "Portable, lags behind"],
        ["Instructor", "Pydantic + patches SDK", "Best of both, extra dep"],
    ],
    col_widths=[220, 280, 420],
)
y += 30
y = pdf.body_text(y, "Instructor patches the native SDK rather than\nreplacing it. You keep full provider access.", size=28)
pdf.footer_text()

# Slide 8: Key Takeaway
pdf.slide_start()
y = 120
y = pdf.tag(y, "The Shift")
y = pdf.accent_line(y)
y = pdf.title_text(y, "LLMs Are Now\nProgrammable Functions", size=48)
y += 30
y = pdf.bullet(y, "Define input (prompt)")
y += 5
y = pdf.bullet(y, "Define output schema (Pydantic)")
y += 5
y = pdf.bullet(y, "Get back validated data")
y += 5
y = pdf.bullet(y, "No regex. No JSON.loads() and pray.")
y += 30
y = pdf.body_text(y, "If you're still parsing free-text with regex, stop.\nStructured output is mature and widely supported.", size=28)
pdf.footer_text()

# Slide 9: CTA
pdf.slide_start()
y = 250
y = pdf.title_text(y, "Full post with code\nexamples and provider details", size=44)
y += 30
y = pdf.accent_line(y, width=CONTENT_W)
y += 20
y = pdf.link_text(y, "dangquan1402.github.io/llm-engineering-notes",
    "https://dangquan1402.github.io/llm-engineering-notes/2026/04/02/structured-output-evolution.html")
y += 40
y = pdf.body_text(y, "What tools are you using for structured output?\nI'd love to hear what's working in your stack.", size=30)
pdf.footer_text("Dquan's LLM Notes  |  @quandang")

# ── Output ──
output_path = os.path.join(OUTPUT_DIR, "002-structured-output-carousel.pdf")
pdf.output(output_path)
print(f"Created: {output_path}")

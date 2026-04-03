#!/usr/bin/env python3
"""Generate LinkedIn carousel for Post 003 — Prompt Caching."""

import os
import subprocess
import tempfile
from carousel_base import CarouselPDF, ACCENT, ORANGE, TEXT, TEXT_LIGHT, CONTENT_W

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
flow_png = os.path.join(OUTPUT_DIR, "003-flow.png")
timeline_png = os.path.join(OUTPUT_DIR, "003-timeline.png")

render_mermaid("""graph LR
    A["System Prompt"] --> B["Tools"]
    B --> C["Messages"]
    C --> D["User Input"]

    style A fill:#2d6a4f,stroke:#1b4332,color:#fff
    style B fill:#40916c,stroke:#2d6a4f,color:#fff
    style C fill:#74c69d,stroke:#40916c,color:#000
    style D fill:#d8f3dc,stroke:#74c69d,color:#000
""", flow_png)

render_mermaid("""timeline
    title Prompt Caching Timeline
    section Google
        Jun 2024 : Context Caching for Gemini
                 : Min 32,768 tokens
                 : ~75% read discount
    section Anthropic
        Aug 2024 : Prompt Caching
                 : Manual breakpoints
                 : 90% read discount
    section OpenAI
        Oct 2024 : Automatic Caching
                 : Zero configuration
                 : 50% read discount
""", timeline_png)

print("Diagrams rendered.")

# ── Build carousel ──
pdf = CarouselPDF()

# Slide 1: Hook
pdf.slide_start()
y = 200
y = pdf.tag(y, "Prompt Caching")
y = pdf.accent_line(y)
y = pdf.title_text(y, "The Hidden Layer\nThat Saves You\n78% on LLM Costs")
y += 40
y = pdf.body_text(y, "Every API call resends the full prompt.\nHere's how to stop paying for it.", size=34)
pdf.footer_text("Dquan's LLM Notes  |  003")

# Slide 2: The Problem
pdf.slide_start()
y = 120
y = pdf.tag(y, "The Problem")
y = pdf.accent_line(y)
y = pdf.title_text(y, "You're paying for the\nsame tokens every call", size=46)
y += 20
y = pdf.body_text(y, "System prompt + tools + history = thousands of tokens.\nIn agentic workflows with 10 tool calls per turn,\nyou're paying 10x for the same prefix.", size=30)
y += 30
y = pdf.stat_box(y, "tokens resent per call in a typical agentic setup", "5,000 - 10,000", color=ORANGE)
y += 10
y = pdf.body_text(y, "Prompt caching: if the prefix hasn't changed,\ndon't reprocess it. Cache and reuse.", size=30)
pdf.footer_text()

# Slide 3: Provider Comparison
pdf.slide_start()
y = 100
y = pdf.tag(y, "Provider Comparison")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Three Approaches", size=42)
y += 20
y = pdf.table(y,
    ["", "Anthropic", "OpenAI", "Google"],
    [
        ["Launch", "Aug 2024", "Oct 2024", "Jun 2024"],
        ["Mode", "Explicit", "Automatic", "Explicit"],
        ["Min tokens", "1,024", "1,024", "32,768"],
        ["Write cost", "+25%", "Free", "Standard"],
        ["Read discount", "90% off", "50% off", "~75% off"],
        ["TTL", "5 min", "~5-60 min", "1 hr+"],
    ],
    col_widths=[200, 240, 240, 240],
)
pdf.footer_text()

# Slide 4: Caching Layers
pdf.slide_start()
y = 100
y = pdf.tag(y, "How It Works")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Caching Is Prefix-Based", size=42)
y += 20
y = pdf.add_image_centered(y, flow_png, max_h=180)
y += 10
y = pdf.table(y,
    ["Layer", "Stability", "Change ="],
    [
        ["System Prompt", "Highest", "Invalidates all"],
        ["Tool Definitions", "High", "Invalidates tools+msgs"],
        ["Message History", "Growing", "Only new re-processed"],
        ["User Message", "None", "Changes every turn"],
    ],
    col_widths=[300, 280, 340],
)
pdf.footer_text()

# Slide 5: Cost Impact
pdf.slide_start()
y = 100
y = pdf.tag(y, "Cost Impact")
y = pdf.accent_line(y)
y = pdf.title_text(y, "10 Calls x 5,000 Token Prefix", size=42)
y += 20
y = pdf.table(y,
    ["", "Anthropic", "OpenAI", "No Cache"],
    [
        ["#1 (cold)", "6,250", "5,000", "5,000"],
        ["#2 (warm)", "500", "2,500", "5,000"],
        ["#3-10 (x8)", "4,000", "20,000", "40,000"],
        ["Total", "10,750", "27,500", "50,000"],
        ["Savings", "78%", "45%", "0%"],
    ],
    col_widths=[220, 240, 240, 220],
)
y += 20
y = pdf.body_text(y, "Anthropic's 90% read discount dominates after 2 calls.\nBreak-even on the 25% write surcharge: request #2.", size=28)
pdf.footer_text()

# Slide 6: Timeline
pdf.slide_start()
y = 100
y = pdf.tag(y, "Timeline")
y = pdf.accent_line(y)
y = pdf.title_text(y, "When Each Provider Shipped", size=42)
y += 20
y = pdf.add_image_centered(y, timeline_png, max_h=500)
pdf.footer_text()

# Slide 7: Practical Rules
pdf.slide_start()
y = 120
y = pdf.tag(y, "Prompt Architecture")
y = pdf.accent_line(y)
y = pdf.title_text(y, "4 Rules for\nCache-Friendly Prompts", size=46)
y += 30
y = pdf.bullet(y, "Keep system prompt stable\n    Any change invalidates everything")
y += 5
y = pdf.bullet(y, "Put tools before messages\n    Tools change less often")
y += 5
y = pdf.bullet(y, "Append, don't rewrite\n    Old messages form a stable prefix")
y += 5
y = pdf.bullet(y, "Same tool order every request\n    Reordering breaks cache")
pdf.footer_text()

# Slide 8: When to Use Which
pdf.slide_start()
y = 120
y = pdf.tag(y, "Which Provider?")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Pick Based on Your Use Case", size=42)
y += 30
y = pdf.bullet(y, "Agentic workflows, many tools\n    Anthropic (90% read discount)", size=28)
y += 10
y = pdf.bullet(y, "Zero-config simplicity\n    OpenAI (automatic, no breakpoints)", size=28)
y += 10
y = pdf.bullet(y, "Massive contexts (docs, codebases)\n    Google (32K min, configurable TTL)", size=28)
y += 40
y = pdf.body_text(y, "Most developers think about what to say.\nHow you structure it matters just as much.", size=30, color=TEXT)
pdf.footer_text()

# Slide 9: CTA
pdf.slide_start()
y = 250
y = pdf.title_text(y, "Full post with code\nexamples and API details", size=44)
y += 30
y = pdf.accent_line(y, width=CONTENT_W)
y += 20
y = pdf.body_text(y, "dangquan1402.github.io/\ncommunity-contributor-posts", size=36, color=TEXT)
y += 40
y = pdf.body_text(y, "Are you using prompt caching in production?\nI'd love to hear how it's affected your costs.", size=30)
pdf.footer_text("Dquan's LLM Notes  |  @quandang")

# ── Output ──
output_path = os.path.join(OUTPUT_DIR, "003-prompt-caching-carousel.pdf")
pdf.output(output_path)
print(f"Created: {output_path}")

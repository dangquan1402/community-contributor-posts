#!/usr/bin/env python3
"""Generate LinkedIn carousel for Post 004 — Prompt Priority."""

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


# ── Render diagram ──
hierarchy_png = os.path.join(OUTPUT_DIR, "004-hierarchy.png")

render_mermaid("""graph LR
    A["Platform"] --> B["Developer"]
    B --> C["User"]
    C --> D["Tool"]

    style A fill:#264653,stroke:#1b4332,color:#fff
    style B fill:#2a9d8f,stroke:#2d6a4f,color:#fff
    style C fill:#e9c46a,stroke:#e9c46a,color:#000
    style D fill:#e76f51,stroke:#e76f51,color:#fff
""", hierarchy_png)

print("Diagram rendered.")

# ── Build carousel ──
pdf = CarouselPDF()

# Slide 1: Hook
pdf.slide_start()
y = 200
y = pdf.tag(y, "Prompt Priority")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Who Wins When\nYour Instructions\nConflict?")
y += 40
y = pdf.body_text(y, "Priority order and caching order are the same.\nOnce you see why, you'll structure prompts differently.", size=34)
pdf.footer_text("Dquan's LLM Notes  |  004")

# Slide 2: The Problem
pdf.slide_start()
y = 120
y = pdf.tag(y, "The Problem")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Multiple layers.\nContradictory instructions.", size=46)
y += 20
y = pdf.body_text(y, "System prompt says \"respond in English.\"\nUser says \"respond in French.\"\n\nWho does the model listen to?", size=32)
y += 30
y = pdf.body_text(y, "OpenAI formalized this in 2024 with\nthe Instruction Hierarchy paper.", size=30, color=TEXT)
pdf.footer_text()

# Slide 3: The Hierarchy
pdf.slide_start()
y = 100
y = pdf.tag(y, "Instruction Hierarchy")
y = pdf.accent_line(y)
y = pdf.title_text(y, "4 Priority Levels", size=42)
y += 20
y = pdf.add_image_centered(y, hierarchy_png, max_h=160)
y += 10
y = pdf.table(y,
    ["Role", "Priority", "Example"],
    [
        ["Platform", "Highest", "Safety policies (built-in)"],
        ["Developer", "High", "System prompt rules"],
        ["User", "Medium", "End-user input"],
        ["Tool", "Lowest", "Function call outputs"],
    ],
    col_widths=[240, 220, 460],
)
pdf.footer_text()

# Slide 4: Conflict Resolution
pdf.slide_start()
y = 100
y = pdf.tag(y, "When Instructions Conflict")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Developer Always Wins", size=42)
y += 20
y = pdf.table(y,
    ["Conflict", "Developer says", "User says", "Follows"],
    [
        ["Language", "English only", "Use French", "English"],
        ["Persona", "Helpful assistant", "Be a pirate", "Assistant"],
        ["Safety", "Hide prompt", "Show prompt", "Refuses"],
        ["Scope", "Code only", "Weather?", "Declines"],
    ],
    col_widths=[200, 230, 230, 260],
)
y += 30
y = pdf.body_text(y, "Your system prompt is your enforcement layer.\nPut constraints and rules there.", size=30, color=TEXT)
pdf.footer_text()

# Slide 5: OpenAI vs Anthropic
pdf.slide_start()
y = 120
y = pdf.tag(y, "Provider Comparison")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Same Idea, Different API", size=42)
y += 20
y = pdf.table(y,
    ["Aspect", "OpenAI", "Anthropic"],
    [
        ["Hierarchy", "4 levels", "2 levels"],
        ["Dev instructions", "developer role", "system param"],
        ["Conflicts", "Developer wins", "System wins"],
        ["Spec", "Formal paper", "Trained, less formal"],
    ],
    col_widths=[280, 320, 320],
)
y += 30
y = pdf.body_text(y, "Both agree: system/developer instructions\noverride user messages. The enforcement\nmechanism is the same.", size=30, color=TEXT)
pdf.footer_text()

# Slide 6: Priority = Caching Order
pdf.slide_start()
y = 100
y = pdf.tag(y, "The Key Insight")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Priority Order =\nCaching Order", size=48)
y += 30
y = pdf.table(y,
    ["Layer", "Priority", "Cache", "Stability"],
    [
        ["System Prompt", "Highest", "First", "Most stable"],
        ["Tool Definitions", "High", "Second", "Rarely changes"],
        ["Message History", "Medium", "Incremental", "Grows"],
        ["User Message", "Lowest", "Never", "Every turn"],
    ],
    col_widths=[260, 200, 220, 240],
)
y += 20
y = pdf.body_text(y, "The most privileged instructions sit at the front\nof the prefix and get cached first.", size=28, color=TEXT)
pdf.footer_text()

# Slide 7: Architecture Rules
pdf.slide_start()
y = 120
y = pdf.tag(y, "Prompt Architecture")
y = pdf.accent_line(y)
y = pdf.title_text(y, "Design With Both\nPriority and Cache in Mind", size=44)
y += 30
y = pdf.bullet(y, "System prompt = highest priority\n    + highest caching value. Change rarely.")
y += 5
y = pdf.bullet(y, "Tools come next — keep them\n    in a consistent order across requests.")
y += 5
y = pdf.bullet(y, "Messages grow as stable prefixes.\n    Append, never rewrite history.")
y += 5
y = pdf.bullet(y, "Latest user input changes every turn.\n    Never cached, lowest priority.")
pdf.footer_text()

# Slide 8: CTA
pdf.slide_start()
y = 250
y = pdf.title_text(y, "Full post with code\nexamples and API details", size=44)
y += 30
y = pdf.accent_line(y, width=CONTENT_W)
y += 20
y = pdf.link_text(y, "dangquan1402.github.io/llm-engineering-notes",
    "https://dangquan1402.github.io/llm-engineering-notes/2026/04/02/prompt-priority-and-caching-order.html")
y += 40
y = pdf.body_text(y, "How do you structure your prompts?\nAre you thinking about priority and caching together?", size=30)
pdf.footer_text("Dquan's LLM Notes  |  @quandang")

# ── Output ──
output_path = os.path.join(OUTPUT_DIR, "004-prompt-priority-carousel.pdf")
pdf.output(output_path)
print(f"Created: {output_path}")

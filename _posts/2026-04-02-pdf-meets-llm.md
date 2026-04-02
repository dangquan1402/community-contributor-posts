---
layout: post
title: "PDF Meets LLM — The Tools, Trade-offs, and Pricing of Document Processing"
date: 2026-04-02
---

PDF processing was one of the first things I worked on as an AI engineer. Back then it was all about OCR pipelines. Now with multimodal LLMs, you can send a document page as an image and ask the model to understand it. But that doesn't mean OCR is dead — far from it.

* TOC
{:toc}

## Native vs Scanned — The First Decision

The first decision in any PDF pipeline: is the document native or scanned?

Native PDFs (digitally created) have embedded text — extract it directly, no OCR, no LLM, no cost. Scanned PDFs are just images in a PDF container — you need OCR or a multimodal LLM to read them.

<pre class="mermaid">
graph LR
    PDF["PDF"] --> CHECK{"Native?"}
    CHECK -->|Yes| TEXT["Direct Text"]
    CHECK -->|No| IMG["Page Images"]
    IMG --> OCR["OCR Service"]
    IMG --> LLM["Multimodal LLM"]
    TEXT --> PIPE["Pipeline"]
    OCR --> PIPE
    LLM --> PIPE

    style PDF fill:#264653,stroke:#264653,color:#fff
    style CHECK fill:#e9c46a,stroke:#e9c46a,color:#000
    style TEXT fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style IMG fill:#e9c46a,stroke:#e9c46a,color:#000
    style OCR fill:#e76f51,stroke:#e76f51,color:#fff
    style LLM fill:#f4a261,stroke:#f4a261,color:#000
    style PIPE fill:#2d6a4f,stroke:#2d6a4f,color:#fff
</pre>

---

## The PDF Processing Toolkit

For native PDFs, the Python ecosystem has solid tools:

| Tool | Type | Best for | Notes |
|---|---|---|---|
| [PyMuPDF [7]](https://pymupdf.readthedocs.io/) (fitz) | Python library | All-in-one (text + manipulation + rendering) | Fast C engine, no external deps |
| [pikepdf [8]](https://pikepdf.readthedocs.io/) | Python library | Low-level PDF surgery, repair, linearization | Built on qpdf, handles corrupted PDFs |
| pypdf | Python library | Simple merge/split/encrypt | Pure Python, was PyPDF2, lightweight |
| ReportLab | Python library | Creating PDFs from scratch | Reports, invoices, charts |
| pdftk | CLI tool | Quick merge/split/rotate/encrypt | The classic, Java dependency |
| qpdf | CLI tool | Page manipulation, repair, linearization | Lightweight, no Java |
| Ghostscript | CLI tool | Compression, format conversion, rendering | Powerful but slow for large batches |

PyMuPDF gives you plain text or line-by-line with bounding boxes (position, font, size) — critical for structured extraction where spatial position determines meaning. pikepdf repairs damaged PDFs and handles low-level surgery. pypdf is the lightweight option for simple merge/split.

```python
# PyMuPDF — text with bounding boxes
import fitz
doc = fitz.open("document.pdf")
for page in doc:
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if block["type"] == 0:
            for line in block["lines"]:
                for span in line["spans"]:
                    text, bbox = span["text"], span["bbox"]

# pikepdf — repair and decrypt
import pikepdf
pdf = pikepdf.open("damaged.pdf")
pdf.save("repaired.pdf")
```

```bash
# CLI tools for shell workflows
pdftk doc1.pdf doc2.pdf cat output merged.pdf
qpdf --empty --pages doc1.pdf 1-5 doc2.pdf 3-10 -- merged.pdf
```

My rule: PyMuPDF when I need text extraction + manipulation together. pikepdf for corrupted files. pypdf for minimal dependencies. pdftk/qpdf for shell one-liners.

---

## Redaction Before External Processing

When dealing with PII, financial data, or medical records, redact before sending documents to any external service. PyMuPDF's `apply_redactions()` actually removes underlying content — not just a black rectangle overlay. Some naive approaches just draw over text, which is still extractable. Redact first, extract second.

---

## PDF to Image — The LLM Bridge

Converting pages to images is essential for feeding documents to multimodal LLMs or OCR services:

```python
import fitz
doc = fitz.open("document.pdf")
page = doc[0]
pix = page.get_pixmap(dpi=300)
image_bytes = pix.tobytes("png")
# Send to any LLM or OCR service
```

Both [Textract [1]](https://aws.amazon.com/textract/pricing/) and [Azure Document Intelligence [2]](https://azure.microsoft.com/en-us/pricing/details/document-intelligence/) support batch document processing, but can be slow for large docs. When you don't need cross-page layout analysis, send pages individually as images for better parallelism and error handling.

---

## LLM Document Understanding — Provider Pricing

Every major LLM provider supports image/document input, but pricing varies wildly. Important: you pay for both input tokens (the image) and output tokens (the extracted text). Most comparisons only show input cost, which is misleading.

Assuming ~500 output tokens per page when extracting text as markdown:

| Provider | Model | Input $/M | Output $/M | Input tokens/page | Total per 1K pages |
|---|---|---|---|---|---|
| [Google [3]](https://ai.google.dev/gemini-api/docs/pricing) | Gemini Flash 2.5 | $0.30 | $2.50 | ~250-500 | ~$1.35-1.40 |
| [OpenAI [5]](https://platform.openai.com/docs/pricing) | GPT-4o-mini | $0.15 | $0.60 | ~765-1,105 | ~$0.41-0.47 |
| [OpenAI [5]](https://platform.openai.com/docs/pricing) | GPT-4o | $2.50 | $10.00 | ~765-1,105 | ~$6.90-7.75 |
| [Anthropic [4]](https://docs.anthropic.com/en/docs/build-with-claude/vision) | Claude Haiku 4.5 | $1.00 | $5.00 | ~1,500-3,000 | ~$4.00-5.50 |
| [Anthropic [4]](https://docs.anthropic.com/en/docs/build-with-claude/vision) | Claude Sonnet 4.6 | $3.00 | $15.00 | ~1,500-3,000 | ~$12.00-16.50 |

**OpenAI** divides images into 512×512 tiles in high detail mode — 170 tokens/tile + 85 base. A typical page (~1024×1024) is ~765 tokens. Low detail: flat 85 tokens.

**Anthropic** extracts text AND converts each page to an image — you pay for both. A 50-page document can consume 75,000-150,000 tokens just in context.

**Gemini** treats each PDF page as one image with fixed token cost — the cheapest LLM option for document processing.

The [OmniAI OCR benchmark [11]](https://getomni.ai/blog/ocr-benchmark) tested 9 providers on 1,000 documents. Gemini Flash achieved the best CER (15%) among multimodal LLMs, vs 25% for GPT-4o. Traditional OCR still leads on pure accuracy, but the gap has narrowed — especially for printed text.

---

## OCR Services — Traditional Extraction Pricing

**[AWS Textract [1]](https://aws.amazon.com/textract/pricing/) (per 1,000 pages, US region):**

| Feature | First 1M pages | After 1M pages |
|---|---|---|
| Detect Text (OCR only) | $1.50 | $0.60 |
| Tables | $15.00 | $10.00 |
| Forms (key-value pairs) | $50.00 | $30.00 |
| Queries (custom questions) | $25.00 | $15.00 |
| Tables + Forms + Queries | $90.00 | $55.00 |

**[Azure Document Intelligence [2]](https://azure.microsoft.com/en-us/pricing/details/document-intelligence/) (per 1,000 pages):**

| Model | Price per 1,000 pages |
|---|---|
| Read (OCR text extraction) | $1.50 |
| Layout (text + tables + structure) | $10.00 |
| Prebuilt (invoices, receipts, IDs) | $10.00 |
| Custom extraction | $25.00 |

Gemini Flash 2.5 at ~$1.35/1K is comparable to basic OCR ($1.50/1K) — but you get document understanding, not just raw text. GPT-4o-mini at ~$0.41/1K is the cheapest overall. Claude Sonnet at ~$12-16.50/1K is 8-10x more expensive than basic OCR.

---

## LLM Extraction vs OCR — The Trade-off

[Gemini's document understanding [3]](https://ai.google.dev/gemini-api/docs/pricing) is impressive for the price:

```python
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content([
    "Extract all text from this document page in markdown format.",
    {"mime_type": "image/png", "data": image_bytes}
])
```

But there's a catch: hallucination. LLMs sometimes add content that isn't there, misread numbers, or reformat in meaning-changing ways. OCR has no hallucination risk — it either reads the character correctly or it doesn't.

---

## OCR + LLM — The Best of Both Worlds

The approach that actually works best for information extraction: combine OCR and LLM. Instead of asking the LLM to both read and understand the document (image → LLM), split the responsibilities: OCR handles reading, LLM handles understanding.

<pre class="mermaid">
graph LR
    IMG["Page Image"] --> OCR["OCR Service"]
    OCR --> TXT["Accurate Text"]
    TXT --> LLM["LLM"]
    LLM --> OUT["Structured Data"]

    style IMG fill:#264653,stroke:#264653,color:#fff
    style OCR fill:#e76f51,stroke:#e76f51,color:#fff
    style TXT fill:#e9c46a,stroke:#e9c46a,color:#000
    style LLM fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style OUT fill:#2d6a4f,stroke:#2d6a4f,color:#fff
</pre>

The naive approach sends the image directly to an LLM — it does OCR and reasoning in one shot. When it fails, you don't know which step failed. Was the text misread, or was the logic wrong?

```python
# Naive: image → LLM (OCR + reasoning in one shot)
response = model.generate_content([
    "Extract invoice number, date, and total.",
    {"mime_type": "image/png", "data": image_bytes}
])
# Risk: misread characters, hallucinated fields

# Better: OCR → text → LLM (separated concerns)
ocr_text = textract_client.detect_document_text(image_bytes)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Extract structured data from this OCR text."},
        {"role": "user", "content": f"Extract invoice number, date, total:\n\n{ocr_text}"},
    ]
)
```

OCR gives you reliable text (no hallucination). LLM operates on text (which it's great at) instead of pixels (where it stumbles). And text tokens are cheaper than image tokens.

| Approach | OCR cost | LLM cost | Total per 1K pages | Accuracy |
|---|---|---|---|---|
| Image → LLM (naive) | $0 | ~$0.23-16.50 | ~$0.23-16.50 | Moderate (hallucination risk) |
| OCR → LLM (combined) | $1.50 | ~$0.05-0.50 | ~$1.55-2.00 | High (no vision errors) |
| OCR → LLM + structured output | $1.50 | ~$0.10-1.00 | ~$1.60-2.50 | Highest (validated schema) |

The sweet spot: basic OCR ($1.50/1K) + GPT-4o-mini for reasoning (~$1.55-2.00 total per 1K pages). For native PDFs, replace OCR with direct text extraction (free).

---

## Decision Framework

| Need | Approach | Cost per 1K pages | Why |
|---|---|---|---|
| Summarize a document | Gemini Flash 2.5 or GPT-4o-mini | ~$0.41-1.35 | Cheapest, good enough |
| Extract text as markdown | Gemini Flash 2.5 or GPT-4o-mini | ~$0.41-1.35 | Competitive quality, comparable to OCR cost |
| Robust entity extraction | OCR + GPT-4o-mini (text) | ~$1.55-2.00 | OCR accuracy + LLM reasoning |
| High-quality understanding | Claude Sonnet or GPT-4o | ~$7-17 | Best reasoning |
| Exact text from native PDFs | PyMuPDF / pypdf | Free | Perfect fidelity |
| Exact text from scanned docs | Textract or Azure (Read) | $1.50 | Reliable, no hallucination |
| Table extraction | Textract or Azure (Layout) | $10-15 | Structured output |
| Forms and key-value pairs | Textract or Azure (Forms) | $10-50 | Accurate but expensive |
| Compliance-critical | OCR + human review | $1.50-50 | Zero hallucination risk |

Always check if the PDF is native first. If it is, you get perfect text for free. For scanned documents, choose based on accuracy needs and budget — LLM for understanding, OCR for fidelity.

What's your PDF processing stack? Are you using LLM-based extraction, or sticking with traditional OCR?

---

References:

[1] ["Amazon Textract — Pricing."](https://aws.amazon.com/textract/pricing/) AWS.  
[2] ["Azure Document Intelligence — Pricing."](https://azure.microsoft.com/en-us/pricing/details/document-intelligence/) Microsoft Azure.  
[3] ["Gemini Developer API — Pricing."](https://ai.google.dev/gemini-api/docs/pricing) Google AI.  
[4] ["Vision — Claude API."](https://docs.anthropic.com/en/docs/build-with-claude/vision) Anthropic.  
[5] ["Pricing."](https://platform.openai.com/docs/pricing) OpenAI.  
[6] ["Images and Vision."](https://platform.openai.com/docs/guides/images-vision) OpenAI.  
[7] ["PyMuPDF Documentation."](https://pymupdf.readthedocs.io/) Artifex.  
[8] ["pikepdf Documentation."](https://pikepdf.readthedocs.io/) pikepdf.  
[9] ["Amazon Textract — Features."](https://aws.amazon.com/textract/features/) AWS.  
[10] ["Document Intelligence — Layout Model."](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/layout) Microsoft Learn.  
[11] ["OmniAI OCR Benchmark."](https://getomni.ai/blog/ocr-benchmark) OmniAI.  

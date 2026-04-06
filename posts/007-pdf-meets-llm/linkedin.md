PDF Meets LLM — The Tools, Trade-offs, and Pricing of Document Processing

PDF processing was one of the first things I worked on as an AI engineer. Now with multimodal LLMs, the landscape has shifted — but OCR isn't dead. The trade-offs are more nuanced than you'd think.

First rule: check if the PDF is native. If yes, extract text directly — free, perfect fidelity. Only reach for OCR or LLMs for scanned documents.

Here's the real cost of LLM text extraction per 1,000 pages (input + output tokens, assuming ~500 output tokens/page for markdown extraction):

→ GPT-4o-mini: ~$0.41-0.47 (cheapest)
→ Gemini Flash 2.5: ~$1.35-1.40
→ Claude Haiku 4.5: ~$4.00-5.50
→ GPT-4o: ~$6.90-7.75
→ Claude Sonnet 4.6: ~$12.00-16.50

Most comparisons only show input token cost — misleading. Output tokens matter, especially for text extraction where you're generating the full page content.

Compare with OCR services:
→ Textract/Azure (text only): $1.50/1K pages
→ Textract/Azure (tables): $10-15/1K
→ Textract (forms): $50/1K
→ Textract (all features): $90/1K

Gemini Flash 2.5 at ~$1.35/1K is comparable to basic OCR ($1.50/1K) — but you get understanding, not just raw text. The OmniAI benchmark shows Gemini Flash at 15% CER — best among multimodal LLMs (GPT-4o: 25% CER).

The catch with naive LLM extraction: hallucination. LLMs sometimes add or misread content when reading from images.

The approach that actually works best for information extraction: OCR + LLM combined. Let OCR handle reading (no hallucination), let LLM handle reasoning (what it's great at). Basic OCR ($1.50/1K pages) + GPT-4o-mini for reasoning = ~$1.55-2.00/1K pages total. Much more robust than sending images directly to an LLM.

The naive image→LLM approach does OCR and reasoning in one shot. When it fails, you don't know which step broke. Separating them gives you accuracy AND debuggability.

Key insight: Anthropic charges for text extraction AND image conversion per page. A 50-page doc can consume 75K-150K tokens just in context. OpenAI uses tile-based pricing (~765 tokens/page). Gemini uses fixed per-page tokens — cheapest by design.

Full post: https://dangquan1402.github.io/llm-engineering-notes/2026/04/02/pdf-meets-llm.html

1/7
Multimodal LLMs can read PDFs now. Does that mean OCR is dead?

No. And the pricing is more surprising than you'd think. A thread:

2/7
First rule: check if the PDF is native (digitally created). If yes, extract text directly — free, perfect fidelity.

Only reach for OCR or LLMs for scanned documents. Most people skip this step.

3/7
LLM text extraction cost per 1,000 pages:

→ GPT-4o-mini: ~$0.45
→ Gemini Flash 2.5: ~$1.35
→ Claude Haiku 4.5: ~$4.00
→ GPT-4o: ~$7.00
→ Claude Sonnet 4.6: ~$14.00

Most comparisons only show input cost. Output tokens matter — you're generating full page content.

4/7
Compare with traditional OCR:

→ Textract/Azure (text only): $1.50/1K pages
→ Textract/Azure (tables): $10-15/1K
→ Textract (forms): $50/1K

Gemini Flash at ~$1.35/1K is cheaper than basic OCR. And you get understanding, not just raw text.

5/7
The catch: LLMs hallucinate when reading images. They add or misread content.

Best approach: OCR + LLM combined.

→ OCR handles reading (no hallucination)
→ LLM handles reasoning (what it's great at)

Cost: ~$1.55-2.00/1K pages. Robust AND cheap.

6/7
Hidden pricing trap with multimodal:

→ Anthropic: charges for text extraction AND image conversion per page. A 50-page doc = 75K-150K tokens in context
→ OpenAI: tile-based pricing (~765 tokens/page)
→ Gemini: fixed per-page tokens — cheapest by design

7/7
Don't send images to LLMs when OCR + LLM gives you accuracy AND debuggability at lower cost.

Full post with pricing tables and benchmarks:
dangquan1402.github.io/llm-engineering-notes/2026/04/02/pdf-meets-llm.html

#LLM #DocumentAI #AI

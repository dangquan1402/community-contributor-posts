1/6
I spent 18 months building RAG pipelines — chunking strategies, hybrid search, threshold tuning.

Then I looked at how Claude Code actually works.

No vector DB. No embeddings. Just grep.

Here's why that changed everything for me:

2/6
We went deep on embedding-based retrieval:
→ Multiple chunking strategies
→ Azure Document Intelligence
→ Hybrid search with BM25

Keywords did most of the heavy lifting. Embeddings helped less than expected.

3/6
The real problem: similarity scores are lossy.

We tried top-N. We tried thresholds. We even tried a two-pass approach — top 100 candidates, then LLM filters for relevance.

It helped, but we were just patching a broken step.

4/6
Claude Code uses zero embeddings.

It transforms your query into search terms, runs grep/glob/file reads, then reasons over results to decide what to look at next.

It's ReAct — the same pattern from LangChain days, but now models are good enough to make it work.

5/6
So I tried it. New chat-with-file project, no embeddings.

Just a ReAct agent with a grep-like tool. No chunking, no vector DB, no thresholds.

It works remarkably well.

6/6
Don't start with the most complex architecture. Start with a capable model, give it search tools, and let it reason.

Full post with diagrams and references:
dangquan1402.github.io/llm-engineering-notes/2026/04/02/why-claude-code-works-and-rag-doesnt-have-to.html

#LLM #RAG #AI

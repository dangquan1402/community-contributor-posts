Why Claude Code Works — And Why You Might Not Need RAG (Embedding) Anymore

I've spent the past year and a half building LLM apps, from RAG (embedding) pipelines to agentic workflows. Here's what shifted my thinking.

Early on, I built chat-with-file systems on PDFs. We went deep on embedding-based retrieval — multiple chunking strategies, document layout tools like Azure Document Intelligence, hierarchical chunking across structured pools, hybrid search with BM25. Keywords did most of the work. Embeddings helped, but less than expected.

Over time I started questioning the core assumption: that embedding space is a good enough representation of our documents. Threshold tuning is painful. Similarity scores and top-N both fall short. We even tried a two-pass approach — top 100 candidates, then LLM filters for relevance. It helped, but we were just patching a lossy retrieval step.

Then I looked at how Claude Code actually works. No vector database. No embeddings. It uses grep, glob, file reads — basic search primitives. It transforms your query into multiple search terms, searches iteratively, and reasons over results to decide what to look at next. It's basically ReAct — the same pattern we tried with LangChain years ago, but now the models are capable enough to make it work.

Recently I started a new chat-with-file project. Inspired by Claude Code, I skipped embeddings entirely. Just a ReAct agent with a grep-like tool. No chunking, no vector DB, no thresholds.

It works remarkably well.

I'm not saying RAG (embedding) is dead. But for many use cases, a capable model with simple search tools can outperform a sophisticated retrieval pipeline.

Don't start with the most complex architecture. Start with a capable model, give it the right tools, and let it reason.

What's your experience? Have you moved from RAG toward agentic approaches?

Full version: github.com/dangquan1402/community-contributor-posts

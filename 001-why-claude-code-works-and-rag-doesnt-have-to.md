# Why Claude Code Works — And Why You Might Not Need RAG Anymore

I've spent the past year and a half building LLM-powered applications — from early RAG pipelines to agentic coding workflows. Here's what I've learned about why Claude Code succeeds where traditional RAG often struggles.

---

## The RAG Era: Embedding Was the Natural First Step

When I first built chat-with-file systems (mostly PDFs), embedding-based retrieval felt like the obvious approach. It addressed two fundamental LLM limitations: context length and the needle-in-a-haystack problem.

We went deep on this:

- **Chunking strategies**: We experimented extensively — fixed-size, semantic, and document-layout-aware chunking using Azure Document Intelligence and AWS Textract. These tools gave us rich metadata: headers, paragraphs, tables, and structural hierarchy.
- **Hierarchical chunking**: I proposed organizing chunks not as a single flat pool, but as multiple structured pools. The intuition is simple — when you go to a library to find a book, you don't search every shelf. You narrow by category, author, and section first. It worked.
- **Hybrid retrieval**: We combined embedding search with keyword search (BM25) and added query transformation. In most cases, keywords did the heavy lifting. Embeddings helped, but not as much as you'd expect.

## Where Embedding Falls Short

Over time, I realized the core assumption behind RAG might be the weakest link: **we assume the embedding space is a good enough representation of our documents.**

The pipeline is straightforward — query → embedding, chunk → embedding, then compare (usually cosine similarity). But the problems compound:

- **Threshold tuning is painful.** Whether you filter by similarity score or top-N, neither is reliable enough across diverse queries.
- **Semantic gaps persist.** Embeddings capture general meaning well, but they miss domain-specific nuance, structural context, and precise intent.

We tried a smarter two-pass approach: retrieve the top 100 candidates, then use an LLM to filter for truly relevant chunks before generating the final answer. It helped — but it also highlighted that we were patching around a fundamentally lossy retrieval step.

## Then Claude Code Changed My Perspective

I've been using Claude Code for almost a year. It has significantly boosted my productivity — I've shipped more in the last year than I expected.

At first, I was explicit about everything: referencing specific folders and files, planning steps, defining conventions upfront. Over time, I realized that with well-structured `CLAUDE.md` files, custom skills, and clear conventions per folder, you can hand Claude the requirements and get solid implementations back.

But the real insight came when I looked at **how Claude Code actually retrieves information.**

It uses tools like `grep`, `glob`, and file reads — basic search primitives. When you ask Claude Code to find something in a codebase, it doesn't embed your code into a vector space. Instead, it:

1. **Transforms your query** into multiple search terms and keywords
2. **Searches iteratively** — file names, function names, then code content
3. **Reasons over the results** and decides what to look at next

This is essentially **ReAct** (Reasoning + Acting) — the same pattern we experimented with early on using LangChain with GPT-3.5 and GPT-4. Back then, the models weren't capable enough to sustain multi-turn reasoning. Every turn went into the scratchpad, and the next call used all accumulated context to derive the next action. It was brittle.

We moved to LangGraph for more deterministic flows — explicit state management, routing, model switching per node. It gave us control. I also built information-gathering agents that worked like interactive forms: the agent keeps asking until all required fields are filled. These patterns had their place.

But the key difference now is **model capability**. With stronger models and longer context windows, the simple loop of *search → read → reason → search again* just works.

## The Takeaway: You Might Not Need Embeddings

Recently, I started a new chat-with-file project. Inspired by Claude Code's approach, I skipped the embedding pipeline entirely. Just a ReAct agent with a grep-like search tool.

It works remarkably well.

No chunking strategies. No embedding models. No similarity thresholds. No vector databases. Just a capable model, a search tool, and the ability to reason over what it finds.

This isn't to say RAG is dead — there are legitimate use cases for vector search at scale. But for many applications, especially those working with structured or semi-structured documents, **the simplest agentic approach might outperform a sophisticated retrieval pipeline.**

The lesson: don't start with the most complex architecture. Start with a capable model, give it the right tools, and let it reason.

---

*What's your experience? Have you moved away from traditional RAG toward agentic approaches? I'd love to hear what's working for you.*

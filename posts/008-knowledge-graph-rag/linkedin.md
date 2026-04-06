Knowledge Graph RAG — The Promise of Structured Retrieval and the Hidden Cost of Building It

My thesis was on knowledge graph embeddings, so when GraphRAG started trending I was genuinely excited. But having lived in that world, I also know what people aren't talking about: the cost of building and maintaining a knowledge graph from scratch.

Traditional RAG chunks documents, embeds them, retrieves top-k. Works great for factual lookups. Falls apart on global questions like "what are the main themes?" or "how are these companies connected?" — no single chunk contains the answer.

GraphRAG (Edge et al., 2024) fixes this: build a knowledge graph from your corpus, detect communities of related entities, generate summaries, answer global questions via map-reduce. Results are compelling — 72-83% win rate on comprehensiveness vs vector RAG.

But here's what the benchmarks don't show: the construction pipeline.

→ Entity extraction: LLM reads every chunk. ~$30 for 2K articles with GPT-4o
→ Entity resolution: "Silicon Valley Bank" vs "SVB" — multi-step dedup, still has failure modes
→ Community detection + summarization: potentially thousands of LLM calls. Total: ~281 min for ~1M tokens

And that's just initial construction.

The real problem is maintenance. Adding new documents means re-extracting entities, resolving against the existing graph, re-running link prediction, entity dedup, re-detecting communities, and re-summarizing (cascades through the hierarchy).

With vector RAG, adding a document = chunk, embed, append. With GraphRAG = potentially restructuring your entire knowledge representation.

And then there's the trend of applying knowledge graphs to source code. Projects like CodexGraph and GraphCoder build KGs from codebases — functions, classes, call graphs, imports — to give LLMs better context.

But code is already structured data. We already have tools that give us the exact same relations:

→ AST (tree-sitter): complete syntactic structure, lossless, free
→ LSP: go-to-definition, find-references, call hierarchy — real-time, free
→ Package managers: dependency graphs, free
→ CodeQL/Semgrep: data flow, taint tracking, free

An LLM-extracted code KG is a lossy, expensive approximation of what these tools provide losslessly. And codebases change with every commit — the maintenance problem is even worse than for documents.

Knowledge graphs make sense for unstructured data with no inherent structure. Code already has structure. Building a KG on top is solving a problem that's already solved.

My take: if you already have a curated knowledge graph, absolutely use it. If you need to build one from scratch, think carefully about whether maintenance cost justifies the improvement. The benchmarks are real, but benchmarks run on static datasets. Production systems don't stay static.

What's your experience with knowledge graphs in production?

Full post: https://dangquan1402.github.io/llm-engineering-notes/2026/04/03/knowledge-graph-rag.html

---
layout: post
title: "Knowledge Graph RAG — The Promise of Structured Retrieval and the Hidden Cost of Building It"
date: 2026-04-03
---

My thesis was on knowledge graph embeddings, so when GraphRAG started trending I was genuinely excited. Finally, knowledge graphs getting the attention they deserve in the LLM era. But having lived in that world, I also know what people aren't talking about: the cost of actually building and maintaining a knowledge graph from scratch.

* TOC
{:toc}

## What Is a Knowledge Graph?

A knowledge graph is a graph where nodes are entities and edges are relations between them. The canonical example is a triple: (Albert Einstein, bornIn, Ulm). Millions of these triples form a structured representation of knowledge — Wikidata has over 100 billion triples. The key property is that knowledge is explicit and traversable. You can follow links, reason over paths, and answer multi-hop questions that would be impossible with flat text.

<pre class="mermaid">
graph LR
    E["Einstein"] -->|bornIn| U["Ulm"]
    E -->|field| P["Physics"]
    E -->|won| NP["Nobel Prize 1921"]
    NP -->|category| P
    U -->|country| DE["Germany"]

    style E fill:#264653,stroke:#264653,color:#fff
    style U fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style P fill:#e9c46a,stroke:#e9c46a,color:#000
    style NP fill:#f4a261,stroke:#f4a261,color:#000
    style DE fill:#2d6a4f,stroke:#2d6a4f,color:#fff
</pre>

---

## Why Traditional RAG Falls Short on Global Questions

Traditional RAG works like this: chunk documents, embed them into vectors, retrieve the top-k most similar chunks for a query. It works well for factual lookups — "what does this API return?" or "what's the refund policy?" But it falls apart on questions that require synthesizing information across many documents. Try asking "what are the main themes in this dataset?" or "how are these companies connected?" — vector similarity doesn't help because no single chunk contains the answer.

---

## The GraphRAG Approach

This is exactly what [GraphRAG (Edge et al., 2024) [1]](https://arxiv.org/abs/2404.16130) addresses. The core idea: build a knowledge graph from your corpus, detect communities of related entities using the [Leiden algorithm [3]](https://arxiv.org/abs/1810.08473), generate summaries for each community, then use those summaries to answer global questions via map-reduce.

<pre class="mermaid">
graph LR
    DOC["Documents"] --> CHUNK["Chunk"]
    CHUNK --> EXT["Extract Entities"]
    EXT --> KG["Knowledge Graph"]
    KG --> COM["Detect Communities"]
    COM --> SUM["Summarize Communities"]
    SUM --> QA["Map-Reduce QA"]

    style DOC fill:#264653,stroke:#264653,color:#fff
    style CHUNK fill:#e76f51,stroke:#e76f51,color:#fff
    style EXT fill:#f4a261,stroke:#f4a261,color:#000
    style KG fill:#e9c46a,stroke:#e9c46a,color:#000
    style COM fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style SUM fill:#40916c,stroke:#40916c,color:#fff
    style QA fill:#2d6a4f,stroke:#2d6a4f,color:#fff
</pre>

The results are compelling. On their benchmarks (~1M token datasets), GraphRAG outperformed vector RAG on comprehensiveness (72-83% win rate) and diversity (62-82% win rate) using LLM-as-judge evaluation. Vector RAG still won on directness — it gives more concise, pointed answers for specific questions. This makes sense: vector RAG is great at finding the needle, GraphRAG is great at describing the haystack.

| Metric | GraphRAG vs Vector RAG | What it means |
|---|---|---|
| Comprehensiveness | 72-83% win | Covers more aspects of the answer |
| Diversity | 62-82% win | Provides more varied perspectives |
| Directness | Vector RAG wins | More concise for specific questions |
| Empowerment | Mixed | Depends on whether quotes or summaries help more |

---

## The Hidden Cost of Building the Knowledge Graph

Here's what it actually takes to go from documents to a usable knowledge graph:

**Step 1: Entity and Relationship Extraction.** An LLM reads every chunk and extracts entities and their relationships. The [Neo4j implementation [2]](https://neo4j.com/blog/developer/global-graphrag-neo4j-langchain/) using LangChain's `LLMGraphTransformer` with GPT-4o extracted ~13,000 entities and ~16,000 relationships from 2,000 news articles. Cost: ~$30, time: ~35 minutes with 10 parallel workers. And this is a small dataset.

```python
# LangChain's LLMGraphTransformer — simplified
from langchain_experimental.graph_transformers import LLMGraphTransformer

transformer = LLMGraphTransformer(llm=ChatOpenAI(model="gpt-4o"))
graph_documents = transformer.convert_to_graph_documents(documents)
# Each document → nodes (entities) + relationships (edges)
```

**Step 2: Entity Resolution.** This is the step the original paper mentions but doesn't ship code for — and it's arguably the hardest. The same entity appears with different names: "Silicon Valley Bank", "Silicon_Valley_Bank", "SVB". You need to deduplicate them. The Neo4j blog's approach: compute text embeddings, build a KNN graph (cosine similarity > 0.95), find connected components, filter by edit distance, then LLM verification for final merge decisions. Even with all that, it still has failure modes for dates, abbreviations, and domain-specific terms.

**Step 3: Community Detection.** Run the Leiden algorithm to partition the graph into hierarchical communities — clusters of closely related entities. The paper's podcast dataset produced communities ranging from 34 (coarsest) to 1,310 (finest). Not every level adds meaningful information — the Neo4j blog found levels 3 and 4 differed by only 4 communities.

**Step 4: Community Summarization.** An LLM generates natural language summaries for each community, bottom-up through the hierarchy. That's potentially thousands of LLM calls. The paper's indexing step took 281 minutes for ~1M tokens of source documents.

| Pipeline Step | What it does | Cost/Complexity |
|---|---|---|
| Entity Extraction | LLM reads every chunk | ~$30 for 2K articles (GPT-4o) |
| Entity Resolution | Deduplicate entities | Multi-step pipeline, domain-dependent |
| Community Detection | Cluster related entities | Needs graph DB ([Neo4j [5]](https://neo4j.com/) + GDS plugin) |
| Community Summarization | LLM summarizes each community | Potentially thousands of LLM calls |
| Total indexing time | End to end | ~281 min for ~1M tokens (paper) |

---

## The Maintenance Problem — What Happens When Knowledge Changes

If you have a fixed, curated knowledge graph — like Wikidata or a domain-specific ontology that rarely changes — GraphRAG works beautifully. The graph is your ground truth, you run community detection once, generate summaries, and you're done. Query-time is efficient: root-level community summaries use 9-43x fewer tokens than processing raw text.

But if you're building the knowledge graph from your own documents — which is the whole point of GraphRAG for most use cases — every update is painful:

Adding new documents means re-extracting entities, but now you need to resolve them against the existing graph. Is "OpenAI" in the new document the same "OpenAI" already in the graph? Probably yes, but what about "GPT-5" vs "GPT 5" vs "the new GPT model"? Every new entity needs link prediction against the full graph.

Entity deduplication gets harder as the graph grows. With 13,000 entities, pairwise comparison is already expensive. At 100K+ entities, you need approximate methods (LSH, blocking strategies), each with its own failure modes.

Community structure shifts. Adding a few hundred nodes can completely reorganize communities, invalidating existing summaries. Do you re-run Leiden on the full graph? Only on affected subgraphs?

Summary staleness. Even if you detect which communities changed, regenerating summaries means more LLM calls. And if higher-level summaries depend on lower-level ones (they do — the paper uses bottom-up summarization), a change at the leaf level cascades through the entire hierarchy.

<pre class="mermaid">
graph LR
    NEW["New Documents"] --> EXT["Re-extract Entities"]
    EXT --> RES["Resolve Against\nExisting Graph"]
    RES --> LINK["Link Prediction"]
    LINK --> DEDUP["Entity Dedup\n(full graph)"]
    DEDUP --> RECOM["Re-detect\nCommunities"]
    RECOM --> RESUM["Re-summarize\n(cascade)"]

    style NEW fill:#e76f51,stroke:#e76f51,color:#fff
    style EXT fill:#f4a261,stroke:#f4a261,color:#000
    style RES fill:#e9c46a,stroke:#e9c46a,color:#000
    style LINK fill:#e9c46a,stroke:#e9c46a,color:#000
    style DEDUP fill:#f4a261,stroke:#f4a261,color:#000
    style RECOM fill:#e76f51,stroke:#e76f51,color:#fff
    style RESUM fill:#e76f51,stroke:#e76f51,color:#fff
</pre>

This is the fundamental tension: GraphRAG converts unstructured data into structured data, and structured data is harder to update than unstructured data. With vector RAG, adding a new document is trivial — chunk it, embed it, append to the index. With GraphRAG, adding a new document means potentially restructuring your entire knowledge representation.

---

## What About Knowledge Graphs for Source Code?

There's another place where knowledge graphs have been proposed recently: source code. Projects like [CodexGraph (Liu et al., 2024) [9]](https://arxiv.org/abs/2408.13689) and [GraphCoder [10]](https://arxiv.org/abs/2404.04862) build knowledge graphs from codebases — extracting entities like functions, classes, and modules, with edges for calls, imports, inheritance, and type relationships — then use graph retrieval to give LLMs better repository-level context.

The idea sounds appealing: code is full of relationships, and understanding a function often means understanding what it calls, what calls it, and what types it uses. A knowledge graph could capture all of that.

But here's my issue: code is already structured data. Unlike natural language documents, source code has a formal grammar. We already have tools that parse it perfectly:

| Tool | What it provides | Maintenance cost |
|---|---|---|
| AST (tree-sitter) | Complete syntactic structure of every file | Zero — deterministic parse |
| LSP | Go-to-definition, find-references, call hierarchy, type info | Zero — runs on-demand from source |
| Package managers | Dependency graphs (pip, npm, cargo) | Zero — reads lockfiles |
| CodeQL / Semgrep | Data flow, taint tracking, control flow graphs | Near-zero — static analysis |

These tools give you the exact same entities and relations that a code knowledge graph would extract — functions, classes, call graphs, import chains, type hierarchies — but with perfect accuracy, zero LLM cost, and no maintenance burden. An AST is a lossless representation of code structure. An LLM-extracted knowledge graph is a lossy, probabilistic approximation of the same thing.

Claude Code's [LSP integration [11]](https://docs.anthropic.com/en/docs/claude-code/overview) is a good example: it can jump to definitions, find all references, and traverse call hierarchies in real time, directly from the source. No graph database, no entity extraction pipeline, no community detection. Just the language server doing what it was designed to do.

<pre class="mermaid">
graph LR
    CODE["Source Code"] --> AST["AST\n(tree-sitter)"]
    CODE --> LSP["LSP\n(definitions, refs)"]
    CODE --> DEP["Dependency\nGraph"]
    CODE --> SA["Static Analysis\n(CodeQL)"]

    KG_APPROACH["LLM-Extracted\nCode KG"]

    AST -->|"lossless, free"| SAME["Same Relations"]
    LSP -->|"real-time, free"| SAME
    DEP -->|"exact, free"| SAME
    SA -->|"precise, free"| SAME
    KG_APPROACH -->|"lossy, $$$"| SAME

    style CODE fill:#264653,stroke:#264653,color:#fff
    style AST fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style LSP fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style DEP fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style SA fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style KG_APPROACH fill:#e76f51,stroke:#e76f51,color:#fff
    style SAME fill:#e9c46a,stroke:#e9c46a,color:#000
</pre>

And the maintenance problem is even worse for code than for documents. Codebases change constantly — every commit modifies functions, adds files, changes call patterns. If maintaining a knowledge graph for a slowly-changing document corpus is already painful, imagine maintaining one for a codebase with dozens of commits per day. Every refactor, every rename, every new dependency would require re-extraction and re-resolution.

The one argument for code KGs is cross-repository or cross-language reasoning — "which services depend on this shared library?" or "how does the Python backend connect to the TypeScript frontend?" LSP doesn't cross language boundaries, and package managers don't trace internal function calls across repos. But even here, tools like [Sourcegraph [12]](https://sourcegraph.com/) solve this with [SCIP-based code intelligence [13]](https://about.sourcegraph.com/blog/announcing-scip) — deterministic, not probabilistic.

My take: knowledge graphs make sense when you're dealing with unstructured data that has no inherent structure. Documents, research papers, news articles — these genuinely benefit from having structure imposed on them. But code already has structure. Building a knowledge graph on top of code is building a lossy approximation of something you can already access losslessly. It's solving a problem that's already solved.

---

## When to Use GraphRAG

| Scenario | Recommendation | Why |
|---|---|---|
| Static knowledge base, global queries | GraphRAG | Upfront cost amortized, global queries excel |
| Rapidly changing documents | Vector RAG | Update cost too high for GraphRAG |
| Specific factual lookups | Vector RAG | No need for global synthesis |
| Existing curated KG (Wikidata, domain ontology) | KG-augmented RAG | Skip the construction step entirely |
| Mixed: some global, some specific | Hybrid | Vector for specific, graph for thematic |

The honest answer for most teams: if you already have a knowledge graph, absolutely use it for retrieval. If you need to build one from scratch for GraphRAG, think very carefully about whether the maintenance cost is worth the improvement over vector RAG. The benchmarks are real — GraphRAG genuinely outperforms on global questions. But benchmarks run on static datasets. Production systems don't stay static.

Tools like [LangChain's LLMGraphTransformer [4]](https://python.langchain.com/docs/how_to/graph_constructing/), [Neo4j [5]](https://neo4j.com/), and [Microsoft's GraphRAG library [6]](https://github.com/microsoft/graphrag) have made the initial construction more accessible. But accessible construction doesn't mean accessible maintenance.

My take: the future of GraphRAG is in incremental graph updates — methods that can add new knowledge without restructuring the entire graph. Some work is happening here ([incremental community detection [7]](https://arxiv.org/abs/2305.14938), [streaming knowledge graph construction [8]](https://arxiv.org/abs/2310.11952)), but it's still early. Until incremental updates are solved, GraphRAG is best suited for corpora that change infrequently and are queried frequently with global, thematic questions.

What's your experience with knowledge graphs in production? Are you building them from scratch or leveraging existing ones?

---

References:

[1] Edge et al. ["From Local to Global: A Graph RAG Approach to Query-Focused Summarization."](https://arxiv.org/abs/2404.16130) arXiv 2024.  
[2] Bratanic, T. ["Implementing 'From Local to Global' GraphRAG with Neo4j and LangChain."](https://neo4j.com/blog/developer/global-graphrag-neo4j-langchain/) Neo4j Blog 2024.  
[3] Traag, V. A. et al. ["From Louvain to Leiden: guaranteeing well-connected communities."](https://arxiv.org/abs/1810.08473) Scientific Reports 2019.  
[4] ["How to construct knowledge graphs."](https://python.langchain.com/docs/how_to/graph_constructing/) LangChain Documentation.  
[5] ["Neo4j Graph Database."](https://neo4j.com/) Neo4j.  
[6] ["GraphRAG."](https://github.com/microsoft/graphrag) Microsoft GitHub.  
[7] Banerjee, P. et al. ["Incremental Community Detection in Distributed Dynamic Graph."](https://arxiv.org/abs/2305.14938) arXiv 2023.  
[8] Chuang, Y. et al. ["Streaming Knowledge Graph Construction."](https://arxiv.org/abs/2310.11952) arXiv 2023.  
[9] Liu et al. ["CodexGraph: Bridging Large Language Models and Code Repositories via Code Graph Databases."](https://arxiv.org/abs/2408.13689) arXiv 2024.  
[10] Liu et al. ["GraphCoder: Enhancing Repository-Level Code Completion via Code Context Graph-based Retrieval and Language Model."](https://arxiv.org/abs/2404.04862) arXiv 2024.  
[11] ["Claude Code Overview."](https://docs.anthropic.com/en/docs/claude-code/overview) Anthropic.  
[12] ["Sourcegraph — Code Intelligence Platform."](https://sourcegraph.com/) Sourcegraph.  
[13] ["Announcing SCIP — a better code indexing format."](https://about.sourcegraph.com/blog/announcing-scip) Sourcegraph Blog.  

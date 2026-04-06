---
layout: post
title: "Prompt Engineering — Why It Works, Not Just How"
date: 2026-04-03
---

There are hundreds of posts about how to write better prompts. This isn't one of them. This post is about why prompts work — what's happening mathematically when you add a system prompt, give few-shot examples, or describe the problem context. Once you understand the mechanism, the "tips and tricks" become obvious consequences.

* TOC
{:toc}

## What an LLM Actually Does

When you send a prompt, every word gets split into tokens, each token gets mapped to an embedding vector, and these vectors flow through dozens of transformer layers — each with multi-head attention and feed-forward networks — until the model produces a probability distribution over the entire vocabulary for the next token. It picks one (with some randomness), appends it, and repeats.

[Stephen Wolfram's deep dive [1]](https://writings.stephenwolfram.com/2023/02/what-is-chatgpt-doing-and-why-does-it-work/) frames this beautifully: the model has learned a compressed representation of the "linguistic manifold" — the lower-dimensional surface in token-space where meaningful text lives. Your prompt defines the starting point on this manifold, and the model follows the most likely trajectory forward.

This is fundamentally different from deterministic systems like linear regression. Even with fixed weights, multiple sources of randomness exist:

| Source | What happens | Why it exists |
|---|---|---|
| Temperature sampling | Logits scaled by T before softmax: $P(\text{token}_i) = \frac{e^{z_i/T}}{\sum_j e^{z_j/T}}$ | T=0 is greedy (repetitive). T>0 allows creative variation |
| [Top-p sampling [2]](https://arxiv.org/abs/1904.09751) | Select smallest token set whose cumulative probability exceeds p | Adapts to model confidence |
| Top-k sampling | Truncate to k highest-probability tokens, renormalize | Prevents sampling from nonsensical tail |
| Hardware non-determinism | GPU floating-point is non-associative: (a+b)+c ≠ a+(b+c) | Parallel matrix multiplications sum in different orders |

The takeaway: an LLM is a probabilistic system. Every prompting technique is about shifting the probability distribution toward the outputs you want.

---

## Why System Prompts Change Everything

The [INSTRUCTOR paper (Su et al., 2022) [3]](https://arxiv.org/abs/2212.09741) gives direct empirical evidence. They trained a single embedding model that produces different embeddings for the same text depending on a prefixed instruction. "The weather is nice today" embedded with "Represent the sentiment:" produces a completely different vector than with "Represent the topic:". Same weights, same input, different geometric location in embedding space.

This happens because instruction tokens participate in self-attention with input tokens. The instruction acts as a learned projection selector — it tells the model which aspects of the input to focus on. A system prompt doesn't just "bias" the output — it fundamentally changes the internal representations.

Think of it like an exam. If a student sees "Chapter 3: Thermodynamics — use formulas 3.1-3.4," they immediately activate relevant knowledge and constrain the search space. The system prompt is the exam header.

---

## The Authority Hierarchy — Why System Prompts Are Special

There's a deeper reason system prompts work, beyond embeddings. Both OpenAI and Anthropic publish specs that define an authority hierarchy for messages:

| Level | [OpenAI Model Spec [24]](https://model-spec.openai.com/2025-04-11.html) | [Anthropic Soul Document [25]](https://www.anthropic.com/news/claude-new-constitution) |
|---|---|---|
| Highest | Platform (model spec rules) | Anthropic (hardcoded behaviors) |
| High | Developer (system prompt) | Operator (system prompt) |
| Medium | User (user messages) | User (user messages) |
| Low | Guideline (default behaviors) | Softcoded defaults |
| None | Tool outputs, quoted text | Untrusted content |

These aren't just documentation — they're training documents. [Anthropic's soul document [25]](https://www.anthropic.com/news/claude-new-constitution) (23,000 words, up from 2,700 in their 2023 constitution) defines Claude's character during training via Constitutional AI. Anthropic even [publishes the system prompts [27]](https://platform.claude.com/docs/en/release-notes/system-prompts) used for claude.ai — you can see exactly what shapes Claude's default behavior.

The hierarchy is baked in through RLHF/RLAIF. Developer/operator messages are binding constraints that user messages cannot override. OpenAI calls this a "chain of command."

This also explains why structured prompts resist prompt injection. Quoted text, JSON, XML, and tool outputs have no authority by default. And [Claude was specifically trained on XML data [28]](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags), making XML tags particularly effective — they activate learned patterns where content between matched tags has a clear semantic role.

---

## Decoder-Only Architecture — Why It Matters

OpenAI and Anthropic use decoder-only [transformers [20]](https://arxiv.org/abs/1706.03762). The system prompt, user message, and model response are all part of a single token sequence processed left-to-right:

```
[system tokens] [user tokens] [assistant tokens →→→ generated one at a time]
```

Each token attends to all previous tokens via causal masking. This is autoregressive generation:

$$P(x_1, \ldots, x_n) = \prod_{t=1}^{n} P(x_t \mid x_1, \ldots, x_{t-1})$$

This differs from [BERT-style [21]](https://arxiv.org/abs/1810.04805) models that use bidirectional attention with masked language modeling + next sentence prediction. [RoBERTa [4]](https://arxiv.org/abs/1907.11692) later showed NSP doesn't help. Decoder-only won because: (1) causal masking naturally supports generation, (2) every token provides a training signal (vs. 15% in MLM), (3) better scaling behavior.

The implication: your prompt is literally part of the sequence being "generated." The model treats it as the beginning of a text it's continuing. This is why format matters — you're writing the first chapter and asking the model to write the next one consistently.

---

## Why Few-Shot Learning Works — The Mathematics

When you include examples in your prompt, the transformer effectively runs an optimization algorithm on those examples during its forward pass.

[Akyürek et al. (2022) [5]](https://arxiv.org/abs/2211.15661) showed that transformer layers implement algorithms equivalent to gradient descent within their forward pass. [Von Oswald et al. (2022) [6]](https://arxiv.org/abs/2212.07677) made this precise: a single self-attention layer can implement one step of gradient descent on in-context examples. Attention keys encode inputs, values encode prediction errors, and the weighted sum computes a gradient update. This isn't a metaphor — it's a mathematical equivalence.

[Garg et al. (2022) [7]](https://arxiv.org/abs/2208.01066) extended this: transformers match optimal algorithms for each function class — OLS for linear regression, Lasso for sparse regression — learned implicitly through pretraining.

The surprising finding: [Min et al. (2022) [8]](https://arxiv.org/abs/2202.12837) tested few-shot examples with random wrong labels. Performance dropped only modestly. What mattered most:

1. The input-label format/structure (what shape the answer should take)
2. The distribution of inputs (what domain we're in)
3. The label space (what the possible outputs are)

Examples activate the right "task circuit" in the model. They're more like a function signature than training data. Mechanistically, [Olsson et al. (2022) [9]](https://arxiv.org/abs/2209.11895) identified "induction heads" — attention patterns that copy patterns from earlier in the context and apply them to the query.

---

## Prompt Techniques — Each One Mapped to Its Mechanism

| Technique | What it does | Why it works (mechanism) | Best for |
|---|---|---|---|
| [Chain of Thought [26]](https://arxiv.org/abs/2201.11903) | "Think step by step" | Intermediate tokens become retrievable context, trading sequence length for computation depth | Multi-step reasoning, math |
| XML/Structured Tags | Wrap content in `<tags>` | Attention boundary signals from HTML/XML training data; separates instructions from data | Complex prompts, injection defense |
| Role Assignment | "You are an expert X" | Shifts conditional distribution: $P(\text{tokens} \mid \text{expert}) \neq P(\text{tokens} \mid \text{generic})$ | Domain-specific tasks |
| Diverse Few-Shot | 3-5 varied examples | Triangulates the task by varying irrelevant dimensions; prevents overfitting to surface features | Classification, extraction |
| Prompt Chaining | Break into subtask pipeline | Focused context per step; errors caught between steps instead of propagating | Complex multi-step tasks |
| [Self-Consistency [23]](https://arxiv.org/abs/2203.11171) | Sample N times, majority vote | Errors are random (different wrong answers), correct reasoning converges | Reasoning, math |
| Self-Critique | "Review your output for X" | Verification easier than generation; reading allows holistic attention over full output | Code review, fact-checking |
| Negative → Positive | "Don't use jargon" → "Use plain language" | Attention has no negation operator; mentioning forbidden concepts activates them | Style, tone, format |

**Chain of Thought** deserves special attention. Transformers are constant-depth computation graphs — each token gets the same number of layers. Without CoT, a model must compress multi-step reasoning into a single forward pass. With CoT, each intermediate result becomes retrievable context for subsequent computation.

**Negative prompting** is particularly interesting. When you write "Don't mention competitors," the tokens "mention" and "competitors" receive attention and activate related representations — increasing their probability. [Anthropic [13]](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) recommends positive framing: instead of "Don't be verbose," say "Respond in exactly 3 sentences."

---

## From Handcrafted to Automated — My Journey

When I worked on text2sql, the early approach was static few-shot: hardcode 3-5 example question-SQL pairs and hope they cover enough patterns. It worked for simple queries but fell apart on anything the examples didn't closely resemble.

The next step was adaptive few-shot — a simple RAG system for examples. Embed all example pairs, retrieve the most similar ones per query. The intuition maps directly to the research: relevant examples activate the most relevant task circuits.

```python
# Static few-shot — same examples for every query
prompt = f"""Convert to SQL:
Q: How many users? SQL: SELECT COUNT(*) FROM users
Q: List all orders SQL: SELECT * FROM orders
Q: {user_query} SQL:"""

# Adaptive few-shot — retrieve relevant examples per query
similar_examples = vector_store.search(user_query, top_k=3)
prompt = f"""Convert to SQL:
{format_examples(similar_examples)}
Q: {user_query} SQL:"""
```

Later, Anthropic released their [Prompt Improver [10]](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver) — a tool that restructures prompts with XML tags, chain-of-thought instructions, and enhanced examples. [OpenAI [11]](https://platform.openai.com/docs/guides/prompt-engineering) has their Prompt Optimizer. [Google [12]](https://ai.google.dev/gemini-api/docs/prompting-strategies) provides detailed documentation but no automated tool.

Now with models like Claude Sonnet 4.6, my workflow is: describe the problem, give examples, pull the [official guidance [13]](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview), and let the model iterate. The models write better prompts than I do. But this only works because the models are now capable enough.

---

## Cross-Provider Comparison

| Aspect | [Anthropic [13]](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) | [OpenAI [11]](https://platform.openai.com/docs/guides/prompt-engineering) | [Google [12]](https://ai.google.dev/gemini-api/docs/prompting-strategies) |
|---|---|---|---|
| Signature technique | XML tags for structure | Delimiters + role hierarchy | Few-shot always recommended |
| Reasoning control | Adaptive thinking with effort parameter | Reasoning models think internally | Explicit planning + self-critique |
| Prompt optimization | [Prompt Improver [10]](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver) | Prompt Optimizer | AI Studio (manual) |
| Long context | Data at top, query at bottom | RAG + reference text | Context first, questions at end |

Despite different approaches, all three converge on the same core: be specific, provide examples, structure input, give context. This makes sense — all three use decoder-only transformers governed by the same mechanisms.

---

## Context Is the Mechanism — From Prompts to Claude Code

Before the LLM era, using Google effectively required the same skill: state your problem clearly, constrain the scope, evaluate results. "My code doesn't work" returns garbage. "Python pandas merge KeyError left_on column not found" returns the exact answer. Input quality determines output quality.

Context is the mechanism. Without it, the model operates in its prior — the average of everything it's seen. With context, you narrow the search space to where useful answers live.

This is why context management in [Claude Code [14]](https://docs.anthropic.com/en/docs/claude-code/overview) matters so much. Claude Code's system prompt is a [modular, conditionally-assembled system [29]](https://code.claude.com/docs/en/how-claude-code-works) — ~2.5K tokens for the base prompt, 14-17K for tool definitions, plus CLAUDE.md, rules, memory, and skills layered on top. When it reads your [CLAUDE.md [15]](https://docs.anthropic.com/en/docs/claude-code/memory), loads [rules [16]](https://docs.anthropic.com/en/docs/claude-code/memory#organize-instructions-with-claude-rules), and checks [memory [15]](https://docs.anthropic.com/en/docs/claude-code/memory) — it's building a prompt. The [context window [17]](https://docs.anthropic.com/en/docs/claude-code/context-window) is the constraint. This is why [best practices [18]](https://docs.anthropic.com/en/docs/claude-code/best-practices) recommend keeping CLAUDE.md under 200 lines and using path-specific rules. It's prompt engineering at the infrastructure level.

<pre class="mermaid">
graph LR
    SYSTEM["System Prompt\n(architecture)"] --> CONTEXT["Context Window"]
    CLAUDE_MD["CLAUDE.md\n(conventions)"] --> CONTEXT
    RULES["Rules\n(path-specific)"] --> CONTEXT
    MEMORY["Memory\n(learned)"] --> CONTEXT
    FILES["Current Files\n(problem)"] --> CONTEXT

    CONTEXT --> ATTENTION["Multi-Head\nAttention"]
    ATTENTION --> OUTPUT["Output\nDistribution"]
    OUTPUT --> RESULT["Generated Code"]

    style SYSTEM fill:#264653,stroke:#264653,color:#fff
    style CLAUDE_MD fill:#264653,stroke:#264653,color:#fff
    style RULES fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style MEMORY fill:#e9c46a,stroke:#e9c46a,color:#000
    style FILES fill:#f4a261,stroke:#f4a261,color:#000
    style CONTEXT fill:#40916c,stroke:#40916c,color:#fff
    style ATTENTION fill:#e76f51,stroke:#e76f51,color:#fff
    style OUTPUT fill:#e9c46a,stroke:#e9c46a,color:#000
    style RESULT fill:#2d6a4f,stroke:#2d6a4f,color:#fff
</pre>

---

## The Bottom Line

Prompt engineering isn't a bag of tricks. It's applied understanding of how transformers process sequences. Every technique that works is a consequence of the architecture — embeddings, attention, and next-token prediction. Understanding the architecture means you can invent new techniques when existing ones don't fit your problem.

What's your approach — do you still handcraft, or have you moved to letting the model iterate?

---

References:

[1] Wolfram, S. ["What Is ChatGPT Doing … and Why Does It Work?"](https://writings.stephenwolfram.com/2023/02/what-is-chatgpt-doing-and-why-does-it-work/) 2023.  
[2] Holtzman et al. ["The Curious Case of Neural Text Degeneration."](https://arxiv.org/abs/1904.09751) ICLR 2020.  
[3] Su et al. ["One Embedder, Any Task: Instruction-Finetuned Text Embeddings."](https://arxiv.org/abs/2212.09741) ACL 2023.  
[4] Liu et al. ["RoBERTa: A Robustly Optimized BERT Pretraining Approach."](https://arxiv.org/abs/1907.11692) 2019.  
[5] Akyürek et al. ["What learning algorithm is in-context learning?"](https://arxiv.org/abs/2211.15661) ICLR 2023.  
[6] Von Oswald et al. ["Transformers Learn In-Context by Gradient Descent."](https://arxiv.org/abs/2212.07677) ICML 2023.  
[7] Garg et al. ["What Can Transformers Learn In-Context?"](https://arxiv.org/abs/2208.01066) NeurIPS 2022.  
[8] Min et al. ["Rethinking the Role of Demonstrations."](https://arxiv.org/abs/2202.12837) EMNLP 2022.  
[9] Olsson et al. ["In-context Learning and Induction Heads."](https://arxiv.org/abs/2209.11895) 2022.  
[10] ["Prompt Improver."](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver) Anthropic.  
[11] ["Prompt Engineering Guide."](https://platform.openai.com/docs/guides/prompt-engineering) OpenAI.  
[12] ["Prompting Strategies."](https://ai.google.dev/gemini-api/docs/prompting-strategies) Google AI.  
[13] ["Prompt Engineering Overview."](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) Anthropic.  
[14] ["Claude Code Overview."](https://docs.anthropic.com/en/docs/claude-code/overview) Anthropic.  
[15] ["Claude Code — Memory."](https://docs.anthropic.com/en/docs/claude-code/memory) Anthropic.  
[16] ["Organize Instructions with .claude/rules."](https://docs.anthropic.com/en/docs/claude-code/memory#organize-instructions-with-claude-rules) Anthropic.  
[17] ["Claude Code — Context Window."](https://docs.anthropic.com/en/docs/claude-code/context-window) Anthropic.  
[18] ["Claude Code — Best Practices."](https://docs.anthropic.com/en/docs/claude-code/best-practices) Anthropic.  
[19] ["Claude Code — Skills."](https://docs.anthropic.com/en/docs/claude-code/skills) Anthropic.  
[20] Vaswani et al. ["Attention Is All You Need."](https://arxiv.org/abs/1706.03762) NeurIPS 2017.  
[21] Devlin et al. ["BERT: Pre-training of Deep Bidirectional Transformers."](https://arxiv.org/abs/1810.04805) NAACL 2019.  
[22] Radford et al. ["Language Models are Unsupervised Multitask Learners."](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) OpenAI 2019.  
[23] Wang et al. ["Self-Consistency Improves Chain of Thought Reasoning in Language Models."](https://arxiv.org/abs/2203.11171) ICLR 2023.  
[24] ["OpenAI Model Spec."](https://model-spec.openai.com/2025-04-11.html) OpenAI 2025.  
[25] ["About Claude."](https://docs.anthropic.com/en/docs/about-claude) Anthropic.  
[26] Wei et al. ["Chain-of-Thought Prompting Elicits Reasoning in Large Language Models."](https://arxiv.org/abs/2201.11903) NeurIPS 2022.  
[27] ["System Prompts — Release Notes."](https://platform.claude.com/docs/en/release-notes/system-prompts) Anthropic.  
[28] ["Use XML Tags to Structure Your Prompt."](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags) Anthropic.  
[29] ["How Claude Code Works."](https://code.claude.com/docs/en/how-claude-code-works) Anthropic.  

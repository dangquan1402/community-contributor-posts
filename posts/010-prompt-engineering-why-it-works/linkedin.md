Prompt Engineering — Why It Works, Not Just How

There are hundreds of posts about how to write better prompts. This isn't one of them. This is about WHY prompts work — what happens mathematically when you add a system prompt, give few-shot examples, or describe context.

An LLM splits text into tokens, maps them to embeddings, flows through transformer layers with multi-head attention, and outputs a probability distribution over the vocabulary. It picks the next token (with randomness), appends it, repeats. Even with fixed weights, temperature sampling, nucleus sampling, and GPU floating-point non-associativity introduce randomness. You're not programming — you're shaping a probability distribution.

Why does a system prompt change everything? The INSTRUCTOR paper (Su et al., 2022) showed the same text produces completely different embeddings depending on a prefixed instruction. Instruction tokens participate in self-attention with input tokens, changing which features the model emphasizes. A system prompt isn't biasing output — it's changing internal representations.

Think of it like an exam header: "Chapter 3: Thermodynamics — use formulas 3.1-3.4." The student already knows the material. The header activates relevant knowledge and constrains the search space.

Both OpenAI and Anthropic publish model specs defining this authority hierarchy: Platform > Developer (system prompt) > User > Defaults. Anthropic's "soul document" (23K words) shapes Claude during training via Constitutional AI. They even publish Claude's system prompts for claude.ai. These hierarchies are trained via RLHF — system prompts are binding instructions that user messages can't override.

Why does few-shot learning work? Transformers implement implicit gradient descent on in-context examples during the forward pass (Akyürek et al., 2022). Surprising finding (Min et al., 2022): examples with random wrong labels barely hurt performance. What matters is the format, domain, and label space — not correctness. Examples activate the right "task circuit" more than they teach.

Each technique maps to a specific mechanism: Chain of Thought gives the model scratch paper (intermediate tokens as retrievable context). XML tags create attention boundary signals. Negative prompting ("Don't do X") backfires because attention has no negation operator — mentioning forbidden concepts activates them. Positive framing ("Do Y") directly specifies the target distribution.

My evolution: static few-shot for text2sql → adaptive few-shot (RAG over examples) → Anthropic's Prompt Improver → now just describe + example + let the model iterate. Models got good enough that natural language context works.

Every technique is ultimately about context — narrowing attention toward the right features. This is why context management in Claude Code matters. CLAUDE.md, rules, memory, skills — they're all building a prompt. It's prompt engineering at the infrastructure level.

What's your approach — still handcrafting, or letting the model iterate?

Full post: https://dangquan1402.github.io/llm-engineering-notes/2026/04/03/prompt-engineering-why-it-works.html

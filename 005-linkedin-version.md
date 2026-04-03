How to Make LLM Output Consistent — Lessons from Building a Scoring System

Run the same prompt twice, get different results. For a chatbot, fine. For a scoring system? Real problem. Here's what I learned building an LLM-as-a-judge system.

1. Temperature is not enough. Temperature=0 uses greedy decoding but it's not truly deterministic — GPU floating-point non-determinism remains. OpenAI's seed param is "best effort" (~85-95% reproducible). Anthropic doesn't even offer seed. Temperature helps, but alone it's insufficient.

2. Check your prompt for conflicts. If your system prompt says "be strict" and a tool says "be lenient," the model oscillates. Ambiguous instructions cause inconsistent output — not randomness, but different interpretations each time. Audit for contradictions.

3. Detailed rubrics per score level. This was the biggest win. Don't say "score 0-10." Define each range: "0-1: completely irrelevant, 2-3: major errors, 4-5: lacks depth..." The Prometheus paper (ICLR 2024) confirmed this dramatically improves consistency. Add 2-3 anchor examples. Use narrow scales (1-5 > 1-10).

4. Chain-of-thought before scoring. G-Eval showed reasoning before scoring improves correlation with human judgments (0.38 → 0.51). Key: reasoning must come BEFORE the score, not after, or it's just post-hoc rationalization.

5. Ensemble multiple calls. Run 3-5 calls, aggregate by median. Use small temperature (0.2-0.3) for useful diversity. Multi-model panels (GPT-4 + Claude + Gemini) reduce shared biases. 3 calls captures most variance reduction.

6. Know the biases: position bias (prefers first response), verbosity bias (longer = higher score), self-preference (~10% boost for own model's output). Mitigate with order-swapping, length normalization, cross-model judging.

Full post: https://dangquan1402.github.io/community-contributor-posts/2026/04/02/llm-consistency-scoring-system.html

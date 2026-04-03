1/7
Run the same LLM prompt twice, get different scores.

For a chatbot, fine. For a scoring system grading thousands of responses? That's a real problem.

Here's what actually works:

2/7
Temperature=0 is not deterministic.

GPU floating-point math introduces noise. OpenAI's seed param gets you ~85-95% reproducibility. Anthropic doesn't even offer seed.

Temperature alone is insufficient.

3/7
The biggest win: detailed rubrics per score level.

Don't say "score 0-10." Define each range:
→ 0-1: completely irrelevant
→ 2-3: major errors
→ 4-5: lacks depth

The Prometheus paper (ICLR 2024) confirmed this dramatically improves consistency.

4/7
Chain-of-thought BEFORE scoring matters.

G-Eval showed reasoning before the score improves correlation with human judgments (0.38 → 0.51).

Key: reasoning must come before the score. After = post-hoc rationalization.

5/7
Ensemble multiple calls. Run 3-5 calls, take the median.

Use small temperature (0.2-0.3) for useful diversity. Multi-model panels (GPT-4 + Claude + Gemini) reduce shared biases.

3 calls captures most variance reduction.

6/7
Know the biases:

→ Position bias: prefers first response
→ Verbosity bias: longer = higher score
→ Self-preference: ~10% boost for own model's output

Mitigate with order-swapping, length normalization, cross-model judging.

7/7
Full post with rubric examples and bias mitigation strategies:
dangquan1402.github.io/community-contributor-posts/2026/04/02/llm-consistency-scoring-system.html

#LLM #AIEngineering #PromptEngineering

---
layout: post
title: "How to Make LLM Output Consistent — Lessons from Building a Scoring System"
date: 2026-04-02
---

If you've worked with LLMs long enough, you've hit this problem: you run the same prompt twice and get different results. For a chatbot, that's fine. For a scoring system where you need reliable, repeatable judgments? It's a real problem.

I've worked on a project using LLM as a judge — a scoring system. Here's everything I've learned about making LLM output consistent.

* TOC
{:toc}

## Temperature Is Not Enough

The first thing most people reach for is temperature. Set it to 0, problem solved, right? Not quite.

Temperature=0 means greedy decoding — the model always picks the highest-probability token. It's the most deterministic setting available, but it's not truly deterministic. GPU floating-point operations are inherently non-deterministic due to parallel reduction — different thread execution orders produce slightly different rounding, which can flip the result when two tokens have near-identical probabilities.

[OpenAI introduced a seed parameter [8]](https://platform.openai.com/docs/guides/text-generation) in late 2023. When you set seed + temperature=0, they aim for deterministic outputs and return a system_fingerprint. But their docs explicitly say it's "best effort." Backend changes, model updates, load balancing across different hardware — all can break reproducibility. In practice, users report 85-95% reproducibility, not 100%.

Anthropic doesn't expose a seed parameter at all. Temperature=0 with greedy decoding is the best you get.

| Parameter | What it does | Deterministic? |
|---|---|---|
| temperature=0 | Greedy decoding, always picks top token | Nearly, but GPU non-determinism remains |
| temperature=0 + seed (OpenAI) | Best-effort determinism with fingerprint tracking | ~85-95% reproducible |
| top_p=1 + temperature=0 | top_p has no effect at temp 0 | Same as temperature=0 |
| Low temperature (0.1-0.3) | Reduces randomness while keeping some diversity | No, but useful for ensembles |

Bottom line: temperature helps, but alone it's not enough for a reliable scoring system.

---

## Audit Your Prompt for Conflicts

The second and most overlooked thing is prompt quality. If your instructions have contradictions or ambiguity, the model will be inconsistent — not because it's random, but because it's interpreting unclear guidance differently each time.

| | Ambiguous Prompt | Clear Prompt |
|---|---|---|
| Criteria | "Score the quality" | "Score 1-5 based on accuracy, completeness, clarity" |
| Examples | None | 2-3 anchor examples with scores and explanations |
| Score range | "Rate 0-10" | Explicit description per level (see below) |
| Result | Model interprets differently each call | Model follows consistent criteria |
| Consistency | Low | High |

Check for conflicts between your system prompt and tool descriptions. If the system prompt says "be strict" and a tool description says "be lenient," the model is stuck. Also check between your rubric criteria — if criterion A rewards brevity and criterion B rewards thoroughness, the model will oscillate.

---

## Detailed Rubrics Per Score Level

The third technique is what made the biggest difference: detailed rubrics with per-score-level descriptions.

If you tell the model "score from 0 to 10," you'll get inconsistent results. The model's idea of a 6 versus a 7 is fuzzy. But if you define exactly what each score range means, consistency improves dramatically.

The [Prometheus paper (Kim et al., ICLR 2024) [4]](https://arxiv.org/abs/2310.08491) showed this rigorously — providing explicit score-level descriptions significantly outperformed generic "rate from 1-5" prompts.

| Technique | Impact on consistency |
|---|---|
| Detailed per-level rubric | High — the single most effective technique |
| 2-3 anchor examples with explanations | High — few-shot calibration teaches the scale |
| Narrower scale (1-5 vs 1-10) | Medium — less ambiguity between adjacent scores |
| Independent sub-criteria scored separately | Medium — reduces conflation of different quality aspects |
| Boundary examples ("this is a 3, this is a 4 because...") | High — resolves edge cases |

---

## Ensemble: Multiple Calls, Aggregate

The fourth technique is ensemble — instead of trusting a single call, run multiple calls and aggregate.

<pre class="mermaid">
graph LR
    subgraph "Single Call"
        S1["One LLM call"] --> S2["Score: 7"]
    end
    subgraph "Ensemble (3 calls)"
        E1["Call 1: Score 7"] --> AGG["Aggregate"]
        E2["Call 2: Score 8"] --> AGG
        E3["Call 3: Score 7"] --> AGG
        AGG --> E4["Final: 7 (median)"]
    end

    style S2 fill:#e9c46a,stroke:#e9c46a,color:#000
    style E4 fill:#2a9d8f,stroke:#2a9d8f,color:#fff
</pre>

| Aggregation method | Best for | Notes |
|---|---|---|
| Mean | Continuous scores | Simple but outlier-sensitive |
| Median | Continuous scores | Robust to outliers, preferred |
| Majority vote | Categorical (pass/fail, A/B/C) | Best for discrete judgments |
| Trimmed mean | Continuous, high stakes | Drop highest and lowest, average the rest |

3 calls captures most of the variance reduction. When ensembling, use a small positive temperature (0.2-0.3) — at temp 0 you'd get the same answer N times. Multi-model panels (GPT-4 + Claude + Gemini) reduce shared biases.

---

## Chain-of-Thought Before Scoring

Chain-of-thought before scoring improves consistency significantly. The [G-Eval paper [3]](https://arxiv.org/abs/2303.16634) showed reasoning before scoring improved correlation with human judgments — Spearman from ~0.38 to ~0.51. The key: reasoning must come before the score, not after. Otherwise it's post-hoc rationalization.

The optimal pattern: chain-of-thought reasoning + structured output for the final score.

Here's what that looks like with Instructor:

```python
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI

class EvaluationStep(BaseModel):
    criterion: str
    observation: str
    score: int = Field(ge=0, le=5)

class Evaluation(BaseModel):
    chain_of_thought: list[EvaluationStep] = Field(
        description="Evaluate each criterion BEFORE assigning final score"
    )
    final_score: int = Field(ge=0, le=10)
    summary: str

client = instructor.from_openai(OpenAI())
result = client.chat.completions.create(
    model="gpt-4o",
    response_model=Evaluation,
    temperature=0,
    messages=[
        {"role": "system", "content": RUBRIC},
        {"role": "user", "content": f"Evaluate: {response_text}"},
    ],
)
```

And for the ensemble:

```python
import statistics

def score_with_ensemble(text, n_calls=3, temperature=0.2):
    scores = []
    for _ in range(n_calls):
        result = client.chat.completions.create(
            model="gpt-4o",
            response_model=Evaluation,
            temperature=temperature,
            messages=[
                {"role": "system", "content": RUBRIC},
                {"role": "user", "content": f"Evaluate: {text}"},
            ],
        )
        scores.append(result.final_score)
    return statistics.median(scores)
```

---

## Known Biases in LLM Scoring

Be aware of known biases in LLM scoring:

| Bias | What happens | Mitigation |
|---|---|---|
| Position bias | Prefers the first response in pairwise comparison | Swap order, average both results |
| Verbosity bias | Rates longer responses higher, even if redundant | Instruct judge to ignore length |
| Self-preference bias | Rates its own model's output ~10% higher | Use a different model as judge |
| Format/style bias | Prefers markdown, bullet points over plain text | Normalize formatting before judging |
| Anchoring bias | Hints about expected quality skew the score | Remove metadata, anonymize outputs |

---

## Putting It All Together

<pre class="mermaid">
timeline
    title Building a Consistent LLM Scoring System
    section Foundation
        Step 1 : Set temperature=0 or low (0.1-0.3 for ensemble)
                : Remove randomness as much as possible
    section Prompt Quality
        Step 2 : Audit prompt for conflicts and ambiguity
                : Ensure system prompt, tools, rubric are aligned
        Step 3 : Write detailed per-score-level rubric
                : Add 2-3 anchor examples with explanations
                : Use narrow scales (1-5) or decomposed sub-criteria
    section Reliability
        Step 4 : Chain-of-thought before scoring
                : Reasoning influences the score, not post-hoc
        Step 5 : Structured output for final score
                : JSON schema with score + reasoning fields
    section Robustness
        Step 6 : Ensemble 3-5 calls, aggregate by median
                : Consider multi-model panel for high stakes
        Step 7 : Monitor score distributions for drift over time
                : Model updates can shift calibration
</pre>

Each layer adds consistency. You don't need all of them for every use case — but for a production scoring system, I'd use at least steps 1-5.

What techniques are you using for LLM consistency? Have you run into the same issues?

---

References:

[1] Zheng et al. ["Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena."](https://arxiv.org/abs/2306.05685) NeurIPS 2023.  
[2] Wang et al. ["Self-Consistency Improves Chain of Thought Reasoning in Language Models."](https://arxiv.org/abs/2203.11171) ICLR 2023.  
[3] Liu et al. ["G-Eval: NLG Evaluation using GPT-4 with Chain-of-Thought and a Form-Filling Paradigm."](https://arxiv.org/abs/2303.16634) 2023.  
[4] Kim et al. ["Prometheus: Inducing Fine-Grained Evaluation Capability in Language Models."](https://arxiv.org/abs/2310.08491) ICLR 2024.  
[5] Wang et al. ["Large Language Models are not Fair Evaluators."](https://arxiv.org/abs/2305.17926) ACL 2024.  
[6] Chan et al. ["ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate."](https://arxiv.org/abs/2308.07201) 2023.  
[7] Wallace et al. ["The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions."](https://arxiv.org/abs/2404.13208) OpenAI, 2024.  
[8] ["Text Generation — Seed Parameter."](https://platform.openai.com/docs/guides/text-generation) OpenAI.  

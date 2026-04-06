1/7
If you're still parsing LLM output with regex, this thread is for you.

We went from "please output JSON" prayers to guaranteed schema-valid responses in 14 months.

Here's the timeline:

2/7
June 2023 — Function calling (OpenAI)
→ Describe functions with JSON Schema
→ Model returns structured arguments
→ Schema-guided but best-effort

First real step. Still unreliable for complex schemas.

3/7
Nov 2023 — JSON mode
→ Guaranteed valid JSON
→ But no schema enforcement

You get valid JSON. Whether it matches YOUR schema? Still a prayer.

4/7
Aug 2024 — Structured Outputs
→ Constrained decoding against your exact schema
→ Output is guaranteed to validate

This was the game changer. LLMs became programmable functions.

5/7
Claude took a different path — forced tool use since April 2024.

No constrained decoding, but reliable in practice. Different mechanism, same result.

6/7
On the tooling side: I moved from LangChain to Instructor (by Jason Liu).

→ Patches native SDKs directly
→ Pydantic models define your schema
→ Validation errors fed back to model for retries

Clean, focused, works across providers.

7/7
The ecosystem converged on Pydantic for schema definition. Write Python, get structured output. Stop writing regex parsers.

Full post with code examples and comparison tables:
dangquan1402.github.io/llm-engineering-notes/2026/04/02/structured-output-evolution.html

#LLM #StructuredOutput #AI

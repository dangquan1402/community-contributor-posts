From Prompt Hacks to Structured Output — How LLMs Learned to Speak JSON

When building software, everything speaks JSON. So when LLMs could only return free-form text, we all hacked around it — injecting prompts like "output in JSON format" with a schema and sample data. Fragile, unreliable, lots of retries.

Then the progression started:

Function calling (June 2023) — OpenAI let you describe functions with JSON Schema. The model returns structured arguments. Schema-guided but best-effort.

JSON mode (Nov 2023) — Guaranteed valid JSON output, but no schema enforcement. You still pray the model follows your structure.

Structured Outputs (Aug 2024) — The game changer. Constrained decoding that guarantees the output validates against your exact schema. LLMs became programmable functions.

Claude took a different path — forced tool use since April 2024. No constrained decoding, but reliable in practice.

On the library side: I started with LangChain for provider abstraction, but hit the lag problem. Working with AWS Bedrock + Claude, it didn't support the latest features. If you stick with one provider, use the native SDK. If you need portability, the abstraction helps. Trade-offs.

I switched to Instructor (by Jason Liu). It patches native SDKs, uses Pydantic models to define output schemas, and retries with validation errors fed back to the model. Clean, focused, works across all providers.

The ecosystem has converged on Pydantic for schema definition — Field descriptions, Literal types for categorical fields, nested models, validators. Write Python, get structured output.

If you're still parsing LLM output with regex, stop. Structured output is mature and widely supported.

What tools are you using for structured output?

Full post: https://dangquan1402.github.io/community-contributor-posts/2026/04/02/structured-output-evolution.html

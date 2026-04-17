1/8
Someone told me: "you need to read the output — generating text doesn't mean anything."

Plug OpenAI API into Claude Code → you get tokens. The loop runs. Tools fire.

Whether any of it is useful? Nobody knows until someone reads it.

2/8
Agent = Model + Harness.

Harness = system prompt + tools + sandbox + context management + middleware.

The part people skip: harnesses aren't portable between models. Each CLI is co-designed with one model.

3/8
Claude Code → TodoWrite, Skills, sub-agents, Sonnet-classifier Auto mode
Codex → apply_patch (V4A format, GPT-5-Codex was post-trained for it)
Gemini CLI → Google Search grounding, leans on 1M context

Different tools. Different assumptions. Different sandboxes.

4/8
apply_patch isn't a generic edit tool.

It's a structured format GPT-5-Codex was explicitly trained to emit.

Hand it to Claude or Gemini → valid patches sometimes. The model wasn't trained for it.

5/8
Sandboxes encode trust assumptions about the model:

→ Codex: mandatory Seatbelt/Landlock — reasoning models run long autonomously
→ Claude Code: permission modes + model-based classifier
→ Gemini: Trusted Folders, lighter

Not security choices. Model choices.

6/8
The hard evidence:

LangChain plugged Claude Opus 4.6 into Codex's harness → 59.6% on Terminal Bench 2.0.

Worse than Codex's own model.

Reason: the harness had been tuned against GPT-5 Codex's specific failure modes. Different model, different failures.

7/8
Three takeaways:

→ No one-size-fits-all harness
→ Model swaps need harness re-tuning, not just an API key change
→ Read the output. Tokens ≠ quality. Loop-completing ≠ work-getting-done

8/8
If you measure agent success by counting successful tool calls or passing tests the agent itself wrote, you might be measuring the harness convincing itself.

Full post: https://dangquan1402.github.io/llm-engineering-notes/2026/04/17/harnesses-arent-portable.html

#LLM #AIAgents #ClaudeCode

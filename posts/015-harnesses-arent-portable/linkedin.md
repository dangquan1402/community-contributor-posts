Someone told me: "you need to read the output — generating text doesn't mean anything."

That line changed how I think about agents.

If I plug the OpenAI API into Claude Code, it absolutely produces tokens. The loop runs, tools fire, files get written. But whether any of it is useful? Nobody knows until someone reads it.

Tokens flowing is not the same as work getting done.

Agent = Model + Harness. The harness is the system prompt, tools, sandbox, context management, middleware. And here's the part that gets skipped: harnesses aren't portable between models.

Claude Code, Gemini CLI, OpenAI Codex CLI — on the surface they all do the same thing. Edit files, run shell commands. Underneath, they're deeply different.

Claude Code leans on TodoWrite, Skills, sub-agents, and a Sonnet-based classifier that decides which tool calls are safe to auto-approve. Anthropic-trained behavior, Anthropic-only components.

Codex ships apply_patch — a V4A structured patch format GPT-5-Codex was specifically post-trained to emit. Hand that same tool to Claude or Gemini and you'll get valid patches sometimes. The model wasn't trained for it.

Gemini CLI has Google Search as a first-class grounding tool and leans on a 1M-token window. Less aggressive compaction, different assumptions about where context lives.

Sandboxes follow the same logic. Codex makes its sandbox mandatory because reasoning models are trusted for long autonomous runs. Claude Code's permission modes assume a different trust profile. Gemini's "Trusted Folders" assumes the big context carries enough state.

The hard evidence: LangChain plugged Claude Opus 4.6 into Codex's harness and scored 59.6% on Terminal Bench 2.0 — worse than Codex's own model. Their explanation: "we didn't run the same Improvement Loop with Claude." The harness had been tuned against one model's failure modes. A different model hits different failure modes.

Three practical takeaways:

There is no one-size-fits-all harness. Every CLI agent is a co-design — tool set, prompt style, sandbox all tuned together.

Model swaps need harness re-tuning. You're not replacing a part, you're rebuilding the scaffolding.

Read the output. The loop completing is not the signal. Tokens are not quality.

If you're measuring agent success by counting successful tool calls or passing tests the agent itself wrote, you might be measuring the harness convincing itself — not the work getting done.

Full post with the architecture comparison table: https://dangquan1402.github.io/llm-engineering-notes/2026/04/17/harnesses-arent-portable.html

What harness-level change has made the biggest quality difference for you?

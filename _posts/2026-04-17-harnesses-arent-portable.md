---
layout: post
title: "Harnesses Aren't Portable — Why Each CLI Agent Has Its Own"
date: 2026-04-17
---

![F1 engine bolted onto a bicycle frame — model without its harness]({{ site.baseurl }}/assets/images/015/hero.jpeg)

Someone told me recently: "you need to read the output — generating text doesn't mean anything." That line stuck. If I plug the OpenAI API into Claude Code, it will absolutely produce tokens. The loop runs, tool calls fire, files get written. But whether any of that is *useful* — whether the work is actually good — nobody knows until someone reads it. Tokens flowing is not the same as work getting done.

* TOC
{:toc}

## Agent = Model + Harness

This is the practical edge of a framing that [LangChain [1]](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) has been pushing: Agent = Model + Harness. "A harness is every piece of code, configuration, and execution logic that isn't the model itself. The model contains the intelligence and the harness is the system that makes that intelligence useful." The harness is the system prompt, the tool set, the sandbox, the context management, the middleware.

And here's the part that matters for anyone building with these tools today: **harnesses aren't portable between models**. Each CLI coding agent — Claude Code, Gemini CLI, OpenAI Codex CLI — is a harness that was co-designed with a specific model. Swap the model out and you get tokens without the quality.

## Three CLIs, Three Harnesses

On the surface these tools all do the same thing: you type, the agent edits files and runs shell commands. Underneath, the architectures are deeply different.

| Dimension | Claude Code | Gemini CLI | OpenAI Codex CLI |
|---|---|---|---|
| Signature tool | `TodoWrite`, Skills, sub-agents (Task) | Google Search grounding as a built-in tool | `apply_patch` (V4A patch format) |
| Memory convention | `CLAUDE.md` re-injected each session | `GEMINI.md` | AGENTS.md, terse system prompts |
| Sandbox | Permission modes + Auto mode (Sonnet classifier approves safe calls) | Trusted Folders, optional container | Mandatory: Seatbelt (macOS) / Bubblewrap+Landlock (Linux) |
| Context strategy | Auto-compact at ~92%, tiered drop/summarize | Leans on 1M-token Gemini 3 window | Assumes reasoning-model internal scratchpad; terse external context |
| Hooks/extensibility | `PreToolUse`, `PostToolUse`, `SessionStart`, MCP, slash commands | MCP, media-gen MCPs (Imagen/Veo/Lyria) | Approval policies: `untrusted`, `on-request`, `never` |

Each of these choices is tuned for one specific model's strengths and quirks.

## The Tools Are Model-Coupled

The clearest evidence is the tools themselves. `apply_patch` in Codex isn't a generic edit tool — it's a [V4A-style structured patch format [2]](https://github.com/openai/codex) that GPT-5-Codex and the o-series were explicitly post-trained to emit correctly. Hand the same tool description to Claude or Gemini and you'll get syntactically valid patches *sometimes*, but the model wasn't trained to reason in that format.

Claude's `TodoWrite` is the mirror image. [It technically does nothing [3]](https://www.langchain.com/blog/deep-agents) — it's a no-op that just writes the plan into the conversation. But Claude models are trained to use it as an externalization anchor during long tasks. Drop `TodoWrite` into a harness around a non-Claude model and it becomes dead weight. The tool only works because the model knows how to use it.

Gemini CLI has Google Search as a first-class grounding tool. Claude Code and Codex don't — they have `WebFetch` and `WebSearch` wrappers, but nothing like native grounding where the model was trained to interleave search calls with generation.

```text
Model-coupled tools (the ones you can't port):

Claude Code    → TodoWrite, Skills, sub-agent Task tool
Gemini CLI     → Google Search grounding
Codex CLI      → apply_patch (V4A format)
```

## Sandboxes Assume a Trust Profile

Sandboxes aren't just security — they're a bet about how the model behaves. Codex makes its sandbox *mandatory* because reasoning models are trusted to plan long autonomous sequences; the sandbox exists precisely so the human doesn't need to approve every step. Claude Code's Auto mode goes the other way: it [uses a Sonnet classifier [4]](https://smartscope.blog/en/generative-ai/claude/claude-code-auto-permission-guide/) to decide which tool calls are safe to auto-approve — which is a harness-level design choice that literally only works because Sonnet is the one classifying. You can't lift that component out and run it in a different harness without bringing the model with it.

Gemini CLI's lighter "Trusted Folders" model reflects a different assumption again — that long context (1M tokens) carries enough of the workspace state that per-call approval adds less value than it costs in friction.

## The Hard Evidence: 59.6%

Principles transfer across harnesses. Performance numbers don't. LangChain ran the experiment directly: they took Claude Opus 4.6 and plugged it into Codex's harness. The result was [59.6% on Terminal Bench 2.0 [5]](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) — worse than Codex's own model on the same harness. Their own explanation: "we didn't run the same Improvement Loop with Claude." The harness had been iteratively tuned against GPT-5 Codex's specific failure modes. A different model hits different failure modes, which the harness was never shaped to catch.

This is the quiet version of the "generating ≠ doing" point. The foreign model's loop completed. Tokens were produced. Tools got called. The score dropped 7+ points anyway.

## Why This Matters in Practice

<pre class="mermaid">
graph LR
    M["Model"] --> H["Harness"]
    H --> O["Output"]
    O -.read.-> V["Verify"]
    V -.tune.-> H

    style M fill:#264653,color:#fff
    style H fill:#2a9d8f,color:#fff
    style O fill:#e9c46a,color:#000
    style V fill:#e76f51,color:#fff
</pre>

Three things follow from this:

1. **There is no one-size-fits-all harness.** Every CLI agent on the market today is a co-design. Picking Claude Code isn't just picking Anthropic's model — it's picking a tool set, prompt style, and sandbox philosophy that were tuned together.
2. **Model swaps need harness re-tuning.** If you want to run a different model through a CLI you love, expect to re-run the improvement loop — new failure modes, new middleware, new system prompt. You're not swapping a part, you're rebuilding the scaffolding.
3. **Read the output.** The loop completing is not the signal. Tokens are not quality. The only way to know if your agent is actually working is to look at what it produced and evaluate it against the task — which, ironically, is the same rule that applies to the humans using these tools.

The uncomfortable implication: if you've been running evals by counting successful tool calls or passing unit tests that the agent itself wrote, you might be measuring the harness convincing itself, not the work getting done.

What harness-level change has made the biggest quality difference for you — a middleware, a sandbox policy, a system-prompt tweak? I'd love to hear what actually moved the needle.

---

References:

[1] Harrison Chase. ["The Anatomy of an Agent Harness."](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) LangChain Blog 2025.  
[2] OpenAI. ["Codex CLI."](https://github.com/openai/codex) GitHub 2025.  
[3] Harrison Chase. ["Deep Agents."](https://www.langchain.com/blog/deep-agents) LangChain Blog 2025.  
[4] ["Claude Code Auto Permission Guide."](https://smartscope.blog/en/generative-ai/claude/claude-code-auto-permission-guide/) SmartScope 2025.  
[5] LangChain Team. ["Improving Deep Agents with Harness Engineering."](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) LangChain Blog 2025.  
[6] OpenAI. ["Codex Sandboxing."](https://developers.openai.com/codex/concepts/sandboxing) OpenAI Developer Docs 2025.  
[7] Google. ["gemini-cli."](https://github.com/google-gemini/gemini-cli) GitHub 2025.  

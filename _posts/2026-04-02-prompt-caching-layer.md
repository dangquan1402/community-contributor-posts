---
layout: post
title: "Prompt Caching — The Hidden Layer That Saves You Money and Time"
date: 2026-04-02
---

If you're building LLM-powered applications and not thinking about prompt caching, you're probably paying more than you need to. This is one of those features that doesn't get enough attention compared to model capabilities, but it has a direct impact on cost and latency.

Let me walk through what I've learned.

---

Every time you make an API call to an LLM, you're sending the full prompt: system instructions, tool definitions, conversation history, and the latest user message. For a multi-turn conversation with a detailed system prompt and 20+ tools, that prefix can be thousands of tokens — and you're paying for all of them on every single call. In agentic workflows where the model makes multiple tool calls per turn, this adds up fast.

Prompt caching solves this. The idea is simple: if the beginning of your prompt hasn't changed since the last call, don't reprocess it. Cache it and reuse it.

---

Here's how the three major providers compare:

| Feature | Anthropic | OpenAI | Google Gemini |
|---|---|---|---|
| Launch | Aug 2024 | Oct 2024 | Jun 2024 |
| Mode | Explicit (manual breakpoints) | Implicit (automatic) | Explicit (cached resource) |
| Min tokens | 1,024 - 2,048 | 1,024 | 32,768 |
| TTL | 5 min (refreshes on hit) | ~5-60 min (automatic) | Configurable (default 1hr) |
| Write cost | +25% surcharge | No surcharge | Standard |
| Read discount | 90% off | 50% off | ~75% off |
| Max breakpoints | 4 per request | N/A | N/A |
| Best for | Agentic workflows, many tools | Zero-config simplicity | Massive contexts (docs, codebases) |

And here's how the prompt layers map to caching priority — the most stable content sits at the top, the most variable at the bottom:

<pre class="mermaid">
graph TD
    A["1. System Prompt -- Most stable, cached first"] --> B["2. Tool Definitions -- Rarely changes mid-conversation"]
    B --> C["3. Message History -- Older messages form stable prefix"]
    C --> D["4. Latest User Message -- Changes every turn, rarely cached"]

    style A fill:#2d6a4f,stroke:#1b4332,color:#fff
    style B fill:#40916c,stroke:#2d6a4f,color:#fff
    style C fill:#74c69d,stroke:#40916c,color:#000
    style D fill:#d8f3dc,stroke:#74c69d,color:#000
</pre>

The cost impact over multiple requests:

<pre class="mermaid">
graph LR
    subgraph "Request 1 (Cold)"
        R1["Full price + write surcharge = cache populated"]
    end
    subgraph "Request 2-4 (Warm)"
        R2["Cache hit on prefix, only new tokens at full price"]
    end
    subgraph "Request 5+ (Savings)"
        R3["90% off Anthropic / 50% off OpenAI / 75% off Google"]
    end
    R1 --> R2 --> R3

    style R1 fill:#e76f51,stroke:#e76f51,color:#fff
    style R2 fill:#f4a261,stroke:#f4a261,color:#000
    style R3 fill:#2a9d8f,stroke:#2a9d8f,color:#fff
</pre>

Now let me go deeper into each provider.

Google was actually first to ship this, launching Context Caching for Gemini in June 2024. But it's designed for a different use case — very large contexts (minimum 32,768 tokens) that persist for hours. You create a cached resource explicitly and reference it across requests. It comes with a storage cost per hour, so it makes sense when you're doing many requests against the same large document or codebase.

Anthropic introduced prompt caching in August 2024, and for me this is where it got interesting. Their approach is manual and explicit. You mark specific points in your prompt with cache_control breakpoints. The system caches everything from the start of the prompt up to each breakpoint. On the next request, if the prefix up to a breakpoint is byte-for-byte identical, you get a cache hit.

The structure follows the natural order of a prompt:

First, the system prompt. This is the most stable part — your instructions, persona, rules. It sits at the very beginning and almost never changes between requests.

Second, tool definitions. If you have tools configured, their descriptions go next. These also tend to be stable across a conversation.

Third, messages. The conversation history, oldest first. As the conversation grows, the older messages form a stable prefix.

Fourth, the latest user message. This changes every turn, so it's almost never cached.

This ordering matters because caching is prefix-based. If you change something early — say you modify the system prompt — everything downstream is invalidated. That's why you want the most stable content at the front and the most variable content at the end.

Anthropic's pricing makes the economics clear: cache writes cost 25% more than normal input tokens, but cache reads are 90% cheaper. So you pay a small premium on the first call, then save dramatically on every subsequent call. For a long system prompt with many tools, the break-even is typically after 2-4 requests. After that, you're saving 50-90% on input costs.

There are some constraints. You need at least 1,024 tokens for Claude 3.5 Sonnet and Opus, or 2,048 for Haiku. You get up to 4 breakpoints per request. And the cache has a 5-minute TTL that refreshes on each hit — so as long as requests keep coming, the cache stays warm.

The latency improvement is significant too. Anthropic reports up to 85% reduction in time-to-first-token for long prompts. In agentic workflows where the model might make 5-10 tool calls in a row, each one reusing the same system prompt and tools, this is a real difference.

---

OpenAI followed in October 2024 with a different philosophy: automatic caching. No breakpoints, no configuration. The system detects when the first 1,024+ tokens of a prompt match a previous request and caches automatically, checking in 128-token increments after that.

The trade-off is different. OpenAI gives you a 50% discount on cache hits with no write surcharge. Less aggressive savings than Anthropic's 90%, but also no upfront cost penalty. You just structure your prompts well and caching happens transparently.

OpenAI explicitly recommends the same prompt ordering — static content like system instructions and tool definitions at the beginning, variable content like user-specific data at the end. Same principle, just automated.

---

The practical takeaway is about prompt architecture. Once you understand that caching is prefix-based, you start designing your prompts differently:

Keep your system prompt stable. Don't inject dynamic data into it unless necessary. Version it carefully. Any change invalidates everything.

Put tool definitions before messages. Tools change less frequently than conversation content. If your tools are deterministically ordered (same order every request), the prefix stays stable through the tools layer.

Append, don't rewrite. For multi-turn conversations, always append new messages. Don't restructure the history. The older messages form a stable prefix that gets cached.

This is also why understanding the caching layer matters when you're choosing between providers or optimizing costs. If you have long, stable system prompts with many tools (think: agentic applications), Anthropic's 90% read discount is extremely aggressive. If you want zero-configuration simplicity and moderate savings, OpenAI's automatic approach is easier to adopt. If you're working with massive contexts (entire codebases, long documents), Google's context caching with configurable TTL might be the right fit.

Most developers I talk to think about prompt engineering in terms of what to say. But how you structure the prompt — what goes where, what stays stable — is just as important for production systems. Caching turns prompt architecture into a cost and performance lever.

Are you using prompt caching in production? I'd love to hear how it's affected your costs.

1/7
Every LLM API call resends the full prompt — system instructions, tools, conversation history.

In agentic workflows with 10 tool calls per turn, you're paying for the same 5,000-token prefix 10 times.

Prompt caching fixes this. Here's what I've learned:

2/7
Caching is prefix-based. The prompt has a natural order:

1. System prompt (most stable)
2. Tool definitions (rarely change)
3. Message history (grows over time)
4. Latest user message (never cached)

Change something early → everything after it is invalidated.

3/7
Anthropic (Aug 2024):
- Manual breakpoints
- 90% read discount, 25% write surcharge
- Break-even after 2 requests
- 5-min TTL, refreshes on hit

For 10 calls with a 5K-token prefix:
50,000 tokens without cache → 10,750 with cache
That's 78% savings.

4/7
OpenAI (Oct 2024):
- Fully automatic, zero config
- 50% read discount, no write surcharge
- Same 10 calls: 27,500 tokens (45% savings)

Lower ceiling but zero effort. Just structure your prompt well and it happens.

5/7
Google (Jun 2024):
- Explicit cached resource
- 32K token minimum
- Configurable TTL, storage cost per hour
- Best for massive contexts (full codebases, long documents)

6/7
4 rules for cache-friendly prompts:

→ Keep system prompt stable (any change invalidates all)
→ Put tools before messages (tools change less)
→ Append, don't rewrite history
→ Same tool order every request (reordering breaks cache)

7/7
Most devs think about what to say in a prompt. How you structure it matters just as much for cost and latency.

Full post with code examples and pricing tables:
dangquan1402.github.io/community-contributor-posts/2026/04/02/prompt-caching-layer.html

#LLM #PromptEngineering #AI

Prompt Caching — The Hidden Layer That Saves You Money and Time

Every LLM API call sends the full prompt: system instructions, tool definitions, conversation history, latest message. In agentic workflows with many tool calls, you're paying for the same prefix thousands of tokens long, over and over.

Prompt caching fixes this. If the beginning of your prompt hasn't changed, don't reprocess it.

The key insight: caching is prefix-based, and prompts follow a natural priority order.

1. System prompt — most stable, cached first
2. Tool definitions — rarely change mid-conversation
3. Messages — older messages form a stable prefix
4. Latest user message — changes every turn, almost never cached

Change something early (like the system prompt), and everything downstream is invalidated.

Anthropic shipped this in August 2024 with manual breakpoints. Cache reads are 90% cheaper than normal input, with a 25% write surcharge. Break-even after 2-4 requests. Up to 85% latency reduction on cache hits.

OpenAI followed in October 2024 with automatic caching — no configuration needed. 50% discount on hits, no write surcharge. Lower ceiling but zero effort.

Google launched Context Caching in June 2024 for massive contexts (32K+ tokens minimum), with configurable TTL and storage costs.

The takeaway: prompt architecture matters for production. Keep system prompts stable. Put tools before messages. Append, don't rewrite history. Structure determines what gets cached.

Most people think about prompt engineering as what to say. But where you put it is just as important for cost and performance.

Full post: https://dangquan1402.github.io/community-contributor-posts/2026/04/02/prompt-caching-layer.html

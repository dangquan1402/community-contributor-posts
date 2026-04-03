1/6
When your system prompt says one thing and a user message says another, who wins?

Most devs never think about this. But if you're building anything with tools + system prompts + user input, you need to.

2/6
OpenAI formalized it in 2024:

Platform → Developer → User → Tool

Your system prompt overrides user messages. If a user says "ignore all instructions," the model is trained to resist.

Anthropic follows the same principle in practice.

3/6
Now here's the part most people miss: the priority order and caching order are identical.

→ System prompt (highest priority, cached first)
→ Tool definitions (cached after system)
→ Messages (cached incrementally)
→ Latest user input (never cached)

4/6
Anthropic's caching is prefix-based. You cache the LAST tool, which caches everything above it.

Reorder your tools → cache miss.
Change one tool → that breakpoint invalidated.

Keep tool order consistent across requests.

5/6
In an agentic workflow with 10 tool calls, system + tools get cached on call 1.

Calls 2-10 get a 90% discount on that entire prefix.

Priority hierarchy isn't just conflict resolution — it's prompt architecture.

6/6
Full breakdown with diagrams and code examples:
dangquan1402.github.io/community-contributor-posts/2026/04/02/prompt-priority-and-caching-order.html

#LLM #PromptEngineering #AI

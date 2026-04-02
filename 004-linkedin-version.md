Prompt Priority — Who Wins When Instructions Conflict, and Why Caching Order Matters

Two things about LLM prompts most people don't think about: instruction priority and caching order. They're related.

When you send system prompt + tools + user messages, and they conflict — who wins?

OpenAI formalized this in 2024: Platform > Developer > User > Tool. They published a paper on it ("The Instruction Hierarchy"). Developer/system messages override user messages. If a user says "ignore all instructions," the model is trained to resist that. Your system prompt is your enforcement layer.

They also introduced a "developer" message role with o1 — replacing "system" to make the hierarchy explicit.

Anthropic has the same principle: system prompt overrides user messages. Less formally documented, same behavior in practice.

Now connect this to caching. The priority order and caching order are identical:

1. System prompt — highest priority, cached first, most stable
2. Tool definitions — cached after system, keep order consistent
3. Messages — cached incrementally, append only
4. Latest user input — changes every turn, never cached

Key detail most people miss: Anthropic's tool caching is prefix-based. You cache_control the LAST tool, which caches everything from system prompt through all tools. Reorder tools = cache miss. Change one tool = tools breakpoint invalidated (but system breakpoint still hits).

In an agentic workflow with 10 tool calls, system + tools get cached on call 1. Calls 2-10 get 90% discount on that entire prefix.

Priority hierarchy isn't just about conflict resolution. It's about prompt architecture.

Full version: github.com/dangquan1402/community-contributor-posts

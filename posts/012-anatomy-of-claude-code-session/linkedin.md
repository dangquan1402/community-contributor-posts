Every Claude Code session assembles ~9 layers of context before you type a word. Most people only know about CLAUDE.md. Here's the full stack — and what you actually control.

The layers, from innermost to outermost:

1. System prompt (Anthropic-controlled, always on) — thousands of tokens of behavioral instructions. This is why Claude Code uses Read instead of cat, pauses before destructive operations, and keeps responses concise. You can't modify it.

2. Built-in tools (always on, permission-controlled) — Read, Write, Edit, Bash, Grep, Glob, Agent, Skill. Always registered. You control access via permission modes (default, auto, plan) and per-tool allow/deny rules in settings.json.

3. Environment context (auto-detected) — git branch, recent commits, OS, shell, working directory. Always on. This is why Claude knows your branch name without being told.

4. CLAUDE.md (loaded when present) — the highest-leverage layer you control. Global (~/.claude/CLAUDE.md), project (./CLAUDE.md), local (.local.md), and rules (.claude/rules/*.md). Team conventions go in project, personal prefs go in global. Keep under 200 lines.

5. Settings (defaults + your overrides) — permissions, hooks, MCP servers, model preferences. Global and project-scoped. The control plane for everything else.

6. Hooks (opt-in) — deterministic shell commands at PreToolUse, PostToolUse, UserPromptSubmit, Stop. Not suggestions — guarantees. The most reliable enforcement mechanism.

7. Skills (discovered when present) — custom slash commands in .claude/skills/. Auto-discovered. Can be user-invocable, model-invocable, or both.

8. MCP servers (opt-in) — external tool integrations. Browser automation, Jira, Figma, databases. Configured in settings.json.

9. Memory (auto when populated) — Claude's persistent notes. Accumulates across sessions. User prefs, project quirks, feedback corrections.

The meta-principle: use CLAUDE.md for guidance, hooks for enforcement, skills for workflows, MCP for capabilities. Instructions can be ignored under pressure. Hooks can't.

Full post with diagrams, code examples, and a practical decision framework: https://dangquan1402.github.io/llm-engineering-notes/2026/04/05/anatomy-of-claude-code-session.html

What layer has been most impactful for your workflow?

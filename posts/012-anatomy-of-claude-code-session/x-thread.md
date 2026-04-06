1/7 Claude Code loads ~9 layers of context before you type anything.

Most people only customize one (CLAUDE.md).

Here's the full stack — and what you actually control. 🧵

2/7 Layers you CAN'T change:
→ System prompt (behavioral instructions from Anthropic)
→ Built-in tools (Read, Edit, Bash, Grep...)
→ Environment detection (git status, OS, branch)

These are why Claude Code "just works" differently from raw Claude.

3/7 Layers you SHOULD change:
→ CLAUDE.md — team conventions (committed to repo)
→ .claude/rules/*.md — scoped by file path
→ ~/.claude/CLAUDE.md — personal preferences

Keep under 200 lines. Push details into rules files.

4/7 Layers for enforcement:
→ Hooks (settings.json) — deterministic shell commands
→ PreToolUse: block dangerous operations
→ PostToolUse: auto-format code
→ Stop: run tests when Claude finishes

Instructions can be ignored. Hooks can't.

5/7 Layers for extension:
→ Skills — custom /slash commands, auto-discovered
→ MCP servers — external tools (Jira, Figma, browsers)
→ Memory — persistent notes across sessions

All opt-in. All configured in settings.json or file conventions.

6/7 Where to put what:
→ Coding standards → CLAUDE.md
→ Hard guardrails → Hooks
→ Reusable workflows → Skills
→ External tools → MCP servers
→ Personal prefs → ~/.claude/CLAUDE.md

7/7 Full breakdown with diagrams and decision framework:

https://dangquan1402.github.io/llm-engineering-notes/2026/04/05/anatomy-of-claude-code-session.html

#ClaudeCode #LLM #DevTools

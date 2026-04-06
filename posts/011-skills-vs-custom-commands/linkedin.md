Skills vs Custom Commands in Claude Code — When to Use Which

If you've been building workflows in Claude Code, you've noticed two ways to create slash commands: Skills (.claude/skills/) and Custom Commands (.claude/commands/). Both create /name in the slash menu. Both accept arguments. So what's the difference?

The short answer: custom commands are the legacy format. Skills are the current standard and a strict superset. The docs are explicit — "Custom commands have been merged into skills. Your existing files keep working. Skills add optional features."

What they share: both are markdown files with YAML frontmatter. Both create slash commands with $ARGUMENTS substitution. Both work at project or personal scope.

Where Skills pull ahead:
- Supporting files: Skills are directories. Include templates, scripts, reference docs alongside SKILL.md. Commands are single files.
- Auto-invocation: Claude can load skills automatically based on description matching. Commands only activate when you type /name.
- Subagent execution: context: fork runs the skill in an isolated context window. Heavy research doesn't bloat your main conversation.
- Dynamic context: !`gh pr diff` injects shell output into the prompt at load time.
- Tool control: allowed-tools restricts what the skill can do. Great for /deploy — only allow specific bash commands.
- Path activation: paths field means the skill only loads when working on matching files.

When to still use commands? Almost never for new work. But if you have working .claude/commands/ files, no urgency to migrate — they'll keep working. Migrate when you need a skill-specific feature.

The real power isn't in either format alone. It's combining skills with hooks for deterministic activation and CLAUDE.md for conventions.

Full post with migration examples and decision flowchart: https://dangquan1402.github.io/llm-engineering-notes/2026/04/03/skills-vs-custom-commands.html

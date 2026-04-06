1/6
Claude Code has two ways to create slash commands: Skills and Custom Commands.

Both create /name in the menu. Both accept arguments.

So when do you use which? Here's the breakdown:

2/6
Custom Commands = single markdown file
→ .claude/commands/review.md
→ Simple prompt template
→ Works fine for basic use

Skills = directory with SKILL.md + supporting files
→ .claude/skills/review/SKILL.md
→ Everything commands do, plus more

3/6
Skills-only features that matter:

→ Auto-invocation: Claude loads skills based on description matching
→ Subagent execution: heavy tasks run in isolated context
→ Dynamic context: !`gh pr diff` injects live data
→ Tool control: restrict what the skill can access

4/6
The biggest practical win: supporting files.

A skill directory can include templates, scripts, reference docs. Claude loads SKILL.md first, digs deeper on demand.

Commands? Everything crammed into one file.

5/6
When to use commands: almost never for new work.

Existing .claude/commands/ files keep working. No urgency to migrate. But for anything new — especially team workflows — default to skills.

6/6
Full post with migration examples, decision flowchart, and side-by-side comparison:
dangquan1402.github.io/llm-engineering-notes/2026/04/03/skills-vs-custom-commands.html

#ClaudeCode #AIEngineering #DeveloperTools

Claude Code as Your Team's Knowledge Layer — CLAUDE.md, Hooks, Skills, and the Onboarding Problem

Think about what happens when a new dev joins your team. Knowledge transfer sessions, architecture walkthroughs, coding conventions, the "we tried X but it didn't work" stories. They spend weeks absorbing tribal knowledge from people's heads and Slack threads.

Now think about starting a new Claude Code session. It reads your CLAUDE.md, loads hooks, discovers skills, checks memory. In seconds, it has context that took the new dev weeks to build.

The interesting part: the infrastructure you build for Claude Code is the exact same infrastructure your team needs for onboarding. (Huge credit to u/JokeGold5455 whose Reddit post and open-source showcase repo inspired much of this — they solo-rewrote ~100K LOC into ~300K LOC over 6 months with Claude Code and shared their complete methodology.)

CLAUDE.md = your coding conventions doc. Committed, version-controlled, reviewed in PRs. When someone updates the convention, everyone (including Claude) gets it. Keep it under 200 lines. Split details into .claude/rules/ with path-specific loading — API conventions only load when working on API files.

Hooks = your CI checks, running locally. Not suggestions — guarantees. PreToolUse hooks block unsafe operations. PostToolUse hooks auto-format code. Stop hooks run tests when Claude finishes. Exit code 2 = blocked, exit code 0 = proceed.

One caveat from u/JokeGold5455's experience: don't run formatters as PostToolUse hooks. Each file modification triggers a system reminder with the diff, eating 160K tokens in a few rounds. Use Stop hooks instead.

Skills = your team's playbooks. Markdown files with slash commands. /deploy runs your deploy procedure step by step. /pr-review injects the PR diff and reviews against your standards. Keep each under 500 lines with progressive disclosure — overview in SKILL.md, deep dives in resources/.

Memory = institutional knowledge. What Claude learns and persists across sessions. Build commands, project quirks, your preferences. Different from CLAUDE.md: that's what you tell Claude. Memory is what Claude tells itself.

The key insight: documentation goes stale because there's no feedback loop. CLAUDE.md has one — when it's wrong, Claude does the wrong thing. Documentation becomes load-bearing, so it actually gets maintained.

The new dev who joins your team doesn't just get a stale wiki page. They get a working system that actively guides their coding assistant toward the team's conventions.

The coding assistant isn't just a tool. It's a forcing function for the practices you already know you should have.

Full post: https://dangquan1402.github.io/community-contributor-posts/2026/04/03/claude-code-as-team-knowledge.html

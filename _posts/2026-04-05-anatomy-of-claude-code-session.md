---
layout: post
title: "Anatomy of a Claude Code Session — What's Built-in, What's Configurable, and What You Control"
date: 2026-04-05
---

Every time you launch Claude Code, a small orchestra of context layers assembles before you type a single character. The system prompt loads. Built-in tools register. Your CLAUDE.md files get read. Skills discover themselves. MCP servers connect. Memory loads from previous sessions. Most of this is invisible — and understanding it tells you where to invest your customization effort.

* TOC
{:toc}

## The Full Stack at a Glance

Here's the layered architecture:

| Layer | Who controls it | Default? | Can disable? |
|---|---|---|---|
| System prompt | Anthropic | Always on | No |
| Built-in tools | Anthropic + you (permissions) | Always on | Partially (permission modes) |
| Environment context | Auto-detected | Always on | No |
| CLAUDE.md files | You (team + personal) | Loaded when present | Don't create the file |
| Settings (settings.json) | You | Defaults apply | Yes — override per key |
| Hooks | You | Off (opt-in) | Yes — remove from settings |
| Skills | You | Discovered when present | Yes — `user-invocable: false` |
| MCP servers | You | Off (opt-in) | Yes — remove from settings |
| Memory | Claude (you direct) | On when configured | Yes — delete memory files |

## Layer 1: The System Prompt

This is the foundation — a large set of instructions that Anthropic injects at the start of every session. You never see it directly (unless you [ask Claude to reflect on it [1]](https://simonwillison.net/2025/Jun/14/claude-code-system-prompt/), or extract it through prompt injection research). It covers:

- Core behavioral instructions — how to approach tasks, when to ask for confirmation, how to handle errors
- Tool usage guidelines — "use Read instead of cat," "use Grep instead of rg," specific protocols for each tool
- Safety rules — what to refuse, how to handle destructive operations, when to confirm before acting
- Git protocols — detailed step-by-step instructions for commits and PRs (this is why Claude Code's git workflow is so consistent)
- Output style — "go straight to the point," "keep responses short and concise," "don't add features beyond what was asked"
- Security awareness — OWASP top 10, command injection prevention, credential handling

The system prompt is substantial — thousands of tokens of carefully tuned instructions. It's why Claude Code behaves differently from raw Claude in the API. You can't modify it, but understanding it explains a lot of Claude Code's default behaviors. For example, the reason Claude Code always uses `Read` instead of `cat` isn't a learned preference — it's an explicit instruction in the system prompt.

One important detail: the system prompt includes a "do not overdo it" philosophy. It explicitly says not to add docstrings, comments, or type annotations to code you didn't change. Not to add error handling for impossible scenarios. Not to create abstractions for one-time operations. If you've noticed Claude Code being more restrained than raw Claude, this is why.

## Layer 2: Built-in Tools

Claude Code ships with a fixed set of tools that are always available:

| Tool | Purpose |
|---|---|
| `Read` | Read files (text, images, PDFs, notebooks) |
| `Write` | Create new files or complete rewrites |
| `Edit` | Exact string replacements in existing files |
| `Bash` | Execute shell commands |
| `Grep` | Search file contents (ripgrep-powered) |
| `Glob` | Find files by pattern |
| `Agent` | Spawn sub-agents for complex tasks |
| `Skill` | Invoke user-defined skills |
| `ToolSearch` | Discover deferred/MCP tools |

These tools are always registered — you can't remove them. But you control *access* through [permission modes [2]](https://docs.anthropic.com/en/docs/claude-code/settings):

| Mode | Behavior |
|---|---|
| `default` | Prompts for approval on potentially risky operations |
| `auto` | Auto-approves most operations (still blocks destructive ones) |
| `plan` | Requires plan approval before execution |
| `bypassPermissions` | No prompts (use with caution) |

You can also set per-tool permissions in `settings.json`:

```json
{
  "permissions": {
    "allow": ["Read", "Grep", "Glob"],
    "deny": ["Bash(rm *)"]
  }
}
```

The permission system is granular — you can allow `Bash` generally but deny specific patterns like `Bash(rm -rf)` or `Bash(git push --force)`.

## Layer 3: Environment Context

Before you type anything, Claude Code auto-detects and injects environment information:

- Working directory and whether it's a git repo
- Current git branch, recent commits, and git status
- Platform (macOS, Linux), shell (bash, zsh), OS version
- Current model name and context window size
- Current date

This is why Claude Code knows your branch name, can reference recent commits, and adapts commands to your OS. It's always on, always fresh per session.

## Layer 4: CLAUDE.md — The Highest-Leverage Layer

This is where you should invest most. Claude Code reads markdown instruction files from multiple locations, layered by scope:

| Scope | Location | Shared with team? | Loaded when? |
|---|---|---|---|
| User (global) | `~/.claude/CLAUDE.md` | No | Every session |
| Project | `./CLAUDE.md` | Yes (committed) | When in project dir |
| Project local | `./CLAUDE.local.md` | No (gitignored) | When in project dir |
| Rules | `.claude/rules/*.md` | Yes (committed) | Based on file paths |

All of these load automatically when they exist. You "disable" them by not having the file. The layering means:

- Team conventions go in `./CLAUDE.md` — committed, version-controlled, reviewed in PRs
- Personal preferences go in `~/.claude/CLAUDE.md` or `./CLAUDE.local.md`
- Topic-specific rules go in `.claude/rules/` — loaded on demand based on which files Claude is working with
- Path-specific rules use frontmatter to scope activation:

```yaml
# .claude/rules/api-conventions.md
---
paths:
  - "src/api/**/*.ts"
---

All API endpoints must validate input with Zod schemas.
```

Practical recommendation from [experienced users [3]](https://www.reddit.com/r/ClaudeCode/comments/1oivs81/claude_code_is_a_beast_tips_from_6_months_of/): keep the main CLAUDE.md under 200 lines. Push details into rules files.

## Layer 5: Settings (settings.json)

The meta-configuration layer. Settings control permissions, hooks, MCP servers, model preferences, and more. They follow the same global/project layering:

| Scope | Location |
|---|---|
| Global | `~/.claude/settings.json` |
| Project (shared) | `.claude/settings.json` |
| Project (local) | `.claude/settings.local.json` |

Settings merge with project settings taking precedence over global. This is the control plane for hooks, MCP, and permissions.

## Layer 6: Hooks — Deterministic Automation (Opt-in)

[Hooks [4]](https://docs.anthropic.com/en/docs/claude-code/hooks) are shell commands that execute at specific points in Claude's workflow. Completely opt-in — nothing runs until you configure it.

| Hook Event | When it fires | Use case |
|---|---|---|
| `PreToolUse` | Before a tool runs | Block unsafe operations, enforce tool preferences |
| `PostToolUse` | After a tool succeeds | Auto-format, lint, log changes |
| `UserPromptSubmit` | When you send a prompt | Inject context, route to skills |
| `Stop` | When Claude finishes responding | Run tests, type-check, verify builds |
| `SubagentStop` | When a sub-agent finishes | Validate sub-agent output |

The key distinction: hooks are *deterministic*. You're not asking Claude to remember to run the linter — you're guaranteeing it runs. A PreToolUse hook can block an operation (exit code 2) or modify it.

Default: nothing. Pure opt-in. But once configured, hooks are the most reliable enforcement mechanism — more reliable than instructions in CLAUDE.md, because they execute as code, not as suggestions.

## Layer 7: Skills — Custom Slash Commands

[Skills [5]](https://docs.anthropic.com/en/docs/claude-code/skills) are markdown files that create slash commands. They live in `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (personal).

Skills are *discovered automatically* when the directory exists. Fine-grained activation controls:

| Control | What it does | Default |
|---|---|---|
| `user-invocable: true` | Shows in slash menu for manual invocation | true |
| `disable-model-invocation: true` | Prevents Claude from auto-activating | false |
| `paths: ["src/**"]` | Only activates for matching files | none (always available) |
| `context: fork` | Runs in isolated sub-agent | false (runs in main context) |

Skills can be model-invocable by default — if your skill's description matches a user request, Claude may auto-activate it. This is powerful but [not 100% reliable [3]](https://www.reddit.com/r/ClaudeCode/comments/1oivs81/claude_code_is_a_beast_tips_from_6_months_of/), which is why the UserPromptSubmit hook pattern exists as a deterministic fallback.

## Layer 8: MCP Servers — External Tool Integrations (Opt-in)

[MCP servers [6]](https://docs.anthropic.com/en/docs/claude-code/mcp-servers) extend Claude Code with external tools — browser automation, database access, Figma integration, Jira, and anything with an MCP adapter.

Purely opt-in. Configured in `settings.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-playwright"]
    }
  }
}
```

Once configured, MCP tools appear alongside built-in tools. Claude discovers them via `ToolSearch` (deferred loading saves context tokens). MCP servers can be scoped globally or per-project.

## Layer 9: Memory — Claude's Persistent Notes

The [memory system [7]](https://docs.anthropic.com/en/docs/claude-code/memory) stores Claude's notes across sessions in `~/.claude/projects/<project-hash>/memory/`.

Memory is a hybrid: the system is always available, but only contains content if Claude (or you) have written to it. The first 200 lines of `MEMORY.md` load automatically at session start. Memory types:

| Type | What it captures | Example |
|---|---|---|
| `user` | Your role, preferences, expertise | "Senior engineer, prefers terse output" |
| `feedback` | Corrections and confirmations | "Don't mock the database in tests" |
| `project` | Ongoing work context | "Merge freeze starts April 5" |
| `reference` | Pointers to external systems | "Bugs tracked in Linear project INGEST" |

## How the Layers Compose

<pre class="mermaid">
graph LR
    SP["System Prompt\n(behavior)"] --> CC["Claude Code\nSession"]
    TOOLS["Built-in Tools\n(capabilities)"] --> CC
    ENV["Environment\n(situation)"] --> CC
    CMD["CLAUDE.md\n(conventions)"] --> CC
    HOOKS["Hooks\n(enforcement)"] --> CC
    SKILLS["Skills\n(workflows)"] --> CC
    MCP["MCP Servers\n(integrations)"] --> CC
    MEM["Memory\n(learnings)"] --> CC

    style SP fill:#264653,stroke:#264653,color:#fff
    style TOOLS fill:#264653,stroke:#264653,color:#fff
    style ENV fill:#264653,stroke:#264653,color:#fff
    style CMD fill:#2a9d8f,stroke:#2a9d8f,color:#fff
    style HOOKS fill:#e76f51,stroke:#e76f51,color:#fff
    style SKILLS fill:#f4a261,stroke:#f4a261,color:#000
    style MCP fill:#e9c46a,stroke:#e9c46a,color:#000
    style MEM fill:#e9c46a,stroke:#e9c46a,color:#000
    style CC fill:#40916c,stroke:#40916c,color:#fff
</pre>

Dark teal nodes are Anthropic-controlled. Green/orange/yellow nodes are yours.

## Practical Decision Framework

| You want to... | Put it in... | Why |
|---|---|---|
| Set coding conventions for the team | `./CLAUDE.md` or `.claude/rules/` | Version-controlled, shared |
| Set personal preferences | `~/.claude/CLAUDE.md` | Applies to all projects |
| Guarantee a check runs | Hooks in `settings.json` | Deterministic, not a suggestion |
| Create a reusable workflow | Skills (`.claude/skills/`) | Discoverable, parameterized |
| Add external tool access | MCP servers in `settings.json` | Extends capability |
| Record project learnings | Memory (let Claude save it) | Persists across sessions |
| Block dangerous operations | PreToolUse hook or permission deny rules | Hard enforcement |
| Scope rules to file types | `.claude/rules/*.md` with `paths:` frontmatter | Loads only when relevant |

## The Meta-Principle

Use instructions (CLAUDE.md) for guidance, hooks for enforcement, skills for workflows, and MCP for capabilities. Instructions can be ignored under pressure. Hooks can't.

The best Claude Code setups treat these layers as complementary, not competing. CLAUDE.md sets the direction. Hooks enforce the guardrails. Skills provide the playbooks. Memory accumulates the context. And the system prompt — the layer you can't touch — provides the behavioral foundation that makes all of it work.

Don't fight the system prompt — work with it. If you want Claude to be more autonomous, adjust permission modes rather than writing "never ask for confirmation" in CLAUDE.md. If you want stricter enforcement, use hooks rather than emphatic instructions.

What layer has been most impactful for your workflow?

---

References:

[1] Simon Willison. ["Claude Code's system prompt."](https://simonwillison.net/2025/Jun/14/claude-code-system-prompt/) simonwillison.net 2025.  
[2] ["Claude Code — Settings."](https://docs.anthropic.com/en/docs/claude-code/settings) Anthropic.  
[3] u/JokeGold5455. ["Claude Code is a Beast — Tips from 6 Months of Hardcore Use."](https://www.reddit.com/r/ClaudeCode/comments/1oivs81/claude_code_is_a_beast_tips_from_6_months_of/) r/ClaudeCode 2025.  
[4] ["Claude Code — Hooks."](https://docs.anthropic.com/en/docs/claude-code/hooks) Anthropic.  
[5] ["Claude Code — Skills."](https://docs.anthropic.com/en/docs/claude-code/skills) Anthropic.  
[6] ["Claude Code — MCP Servers."](https://docs.anthropic.com/en/docs/claude-code/mcp-servers) Anthropic.  
[7] ["Claude Code — Memory, CLAUDE.md, and .claude/rules."](https://docs.anthropic.com/en/docs/claude-code/memory) Anthropic.  
[8] ["Claude Code — Overview."](https://docs.anthropic.com/en/docs/claude-code/overview) Anthropic.  
[9] ["Claude Code — Sub-agents."](https://docs.anthropic.com/en/docs/claude-code/sub-agents) Anthropic.  

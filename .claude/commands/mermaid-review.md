Review and improve mermaid diagrams in the specified post. Apply these guidelines:

## Diagram Type Selection

- `timeline` — for chronological progressions/evolution (e.g., feature launch dates, technology adoption phases)
- `graph LR` — for flows, pipelines, priority chains, or cycles with feedback loops. Keep labels SHORT (1-3 words per node)
- `graph TD` — avoid in most cases. Only use for deep decision trees with 4+ branching levels
- Tables — preferred over diagrams when showing comparisons, feature matrices, or data with multiple attributes per item

## When to Use a Table Instead of a Diagram

Replace a diagram with a table when:
- The diagram has long text labels that get cramped
- The content is a comparison (A vs B, before/after, provider differences)
- Each item has multiple attributes (a table row handles this naturally, a graph node doesn't)
- The diagram is two disconnected chains side by side (e.g., "bad path" vs "good path")
- The diagram is essentially a list rendered vertically

## When to Keep a Diagram

Keep a diagram when:
- Showing a flow with a feedback loop or cycle (e.g., search → read → enough? → retry)
- Showing a pipeline with clear directionality (A → B → C → D)
- The visual shape itself communicates meaning (gradient, hierarchy, branching)

## Graph Diagram Rules

- Labels: 1-3 words per node. Put details in surrounding text or a companion table
- `graph LR` for linear flows and cycles. Compact and reads naturally left-to-right
- Color palette:
  - Green: `fill:#2a9d8f`, `fill:#2d6a4f`, `fill:#40916c` (positive/final states)
  - Red/orange: `fill:#e76f51`, `fill:#f4a261` (problem/initial states)
  - Yellow: `fill:#e9c46a` (decisions/intermediate)
  - Dark: `fill:#264653` (neutral/start)
- Green gradients (dark to light) for showing stability/priority spectrums

## Timeline Diagram Rules

- Use `section` to group related events
- Include key details as sub-items under each date
- No manual styling needed — sections auto-color

## Concrete Examples (before/after)

Before (bad — long labels in graph TD):
```
graph TD
    A["Ambiguous Prompt -- Vague criteria, no examples"] --> B["Model interprets differently"]
    B --> C["Inconsistent scores"]
```
After (good — table for comparison):
```
| | Ambiguous Prompt | Clear Prompt |
|---|---|---|
| Criteria | "Score the quality" | "Score 1-5 based on accuracy, completeness, clarity" |
| Result | Inconsistent | Consistent |
```

Before (bad — verbose graph TD for priority list):
```
graph TD
    A["1. System Prompt -- Most stable, cached first"] --> B["2. Tool Definitions -- Rarely changes"]
```
After (good — table + compact graph LR):
```
| Layer | Priority | Stability |
|---|---|---|
| System Prompt | Highest | Most stable |
| Tools | High | Rarely changes |

graph LR
    A["System Prompt"] --> B["Tools"] --> C["Messages"] --> D["User Input"]
```

Before (bad — subgraphs with long text for cost comparison):
```
graph LR
    subgraph "Request 1 (Cold)"
        R1["Full price + write surcharge = cache populated"]
    end
```
After (good — concrete numbers in a table):
```
| Request | Anthropic | OpenAI |
|---|---|---|
| #1 (cold) | 5,000 × 1.25x = 6,250 | 5,000 × 1.0x = 5,000 |
| #2+ (warm) | 5,000 × 0.1x = 500 | 5,000 × 0.5x = 2,500 |
```

## Rendering

- Full posts (.md): use fenced ` ```mermaid ` code blocks
- Jekyll posts (_posts/): use `<pre class="mermaid">` tags

## Process

1. Read the specified post file(s)
2. Identify each diagram
3. For each: decide if it should stay as a diagram, become a table, or become diagram + table
4. Apply the rules above
5. Update both the full post and the Jekyll post

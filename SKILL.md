# Ollama Worker Skill

Delegate tasks to Ollama models (local or cloud) while maintaining quality oversight.

**Default model:** `kimi-k2.5:cloud` — multimodal, thinking, tools, near-Claude quality

## Architecture

```
You (Claude) — Orchestrator & Quality Control
    ├── Claude sub-agents — Complex multi-step work
    └── Ollama workers — Simple/bulk tasks (this skill)
```

**Key principle:** You always review Ollama output before using it or showing it to the user.

## Quick Start

```bash
# Basic delegation (uses kimi-k2.5:cloud by default)
python3 ~/clawd/skills/ollama-worker/worker.py delegate --task "Summarize this"

# With thinking mode (shows reasoning)
python3 ~/clawd/skills/ollama-worker/worker.py delegate --think --task "Solve this problem"

# With image input (vision)
python3 ~/clawd/skills/ollama-worker/worker.py delegate --image photo.jpg --task "Describe this"

# With specific model
python3 ~/clawd/skills/ollama-worker/worker.py delegate --model glm-4.7:cloud --task "..."
```

## Features

### 🐝 Agent Swarm Mode (`--swarm`)
**The killer feature.** Triggers Kimi's internal agent orchestration via prompt engineering.

```bash
worker.py delegate --swarm --task "Design a complete system for X"
worker.py delegate --swarm --agents 5 --task "..."  # Control agent count
```

What happens:
1. Kimi decomposes your task into specialized sub-tasks
2. Spawns named agents (Agent-1, Agent-2, etc.) with domain expertise
3. Each agent provides independent analysis
4. Synthesis Coordinator integrates findings
5. Output wrapped in `[ORCHESTRATION PROTOCOL INITIATED]` ... `[ORCHESTRATION COMPLETE]`

Great for: architecture design, multi-faceted research, competitive analysis, complex decisions.

**Discovery:** This isn't true parallel execution — it's prompt-triggered structured thinking that produces dramatically better output for complex tasks.

### Thinking Mode (`--think`)
Enables step-by-step reasoning. The model's thought process appears in stderr, clean answer in stdout.
Great for: math, logic, complex analysis, verifying the model isn't bullshitting.

Note: `--swarm` automatically enables thinking mode.

### Vision (`--image path`)
Pass an image for multimodal analysis. Supports: jpg, png, gif, webp.
Great for: image description, OCR, visual Q&A, analyzing screenshots.

### Tool Calling (`--tools tools.json`)
Provide a JSON file with tool definitions. Model will output tool calls if appropriate.
Great for: structured extraction, agentic workflows.

### JSON Output (`--json`)
Forces valid JSON output.
Great for: data extraction, structured responses.

## Model Selection Guide

| Model | Speed | Quality | Features | Best For |
|-------|-------|---------|----------|----------|
| phi3:mini | ⚡⚡⚡ | ⭐⭐ | basic | Quick utilities |
| llama3:8b | ⚡⚡ | ⭐⭐⭐ | basic | Local general tasks |
| glm-4.7:cloud | ⚡⚡ | ⭐⭐⭐⭐ | tools | Creative, coding |
| **kimi-k2.5:cloud** | ⚡ | ⭐⭐⭐⭐⭐ | vision, tools, thinking | Default — best quality |

**Cloud models need `:cloud` suffix** and require `ollama signin`.

## When to Delegate

**Good candidates:**
- Summarization (long docs, articles, transcripts)
- Draft generation (variations, boilerplate, first drafts)
- Data extraction (parse structure from text)
- Bulk classification/tagging
- Image analysis (with vision)
- Math/logic with verification (with thinking)
- Code scaffolding

**Keep for yourself:**
- Multi-step tool use chains
- Tasks requiring your full context
- Final user-facing responses
- Anything where errors have real consequences

## Workflow

1. Identify a delegatable task
2. Pick features: `--think` for reasoning, `--image` for vision, `--json` for structured
3. Call worker.py with clear instructions
4. **Review the output** — check for hallucinations, errors, missing info
5. Use, refine, or redo yourself if quality is lacking
6. Never pass raw unreviewed output to user

## Stats & Logging

```bash
# View delegation statistics
python3 ~/clawd/skills/ollama-worker/worker.py stats
```

Logs all delegations to `~/clawd/logs/ollama-delegations.jsonl` with:
- Model used, tokens in/out, elapsed time
- Whether thinking/vision/tools were used

## Tips

- **Be specific** — Ollama models need clear guidance
- **Use thinking mode** for anything requiring reasoning
- **Verify JSON output** — ask for JSON, validate it parses
- **Chain delegations** — draft with Ollama, refine yourself
- **Check the logs** — track what's working, what's not

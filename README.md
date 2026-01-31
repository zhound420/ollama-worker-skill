# Ollama Worker

> **Claude as orchestrator, Ollama as worker, mandatory QC before delivery.**

> **Level up:** When you're ready for autonomous agent-to-agent orchestration and swarm intelligence, see [a2a-agents](https://github.com/zhound420/a2a-agents-skill).

A Clawdbot skill for delegating tasks to Ollama models while maintaining quality oversight. The key insight: let cheap/fast models handle bulk work, but always have Claude review before the user sees anything.

## The Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  Claude (Opus/Sonnet) — Orchestrator & Quality Control      │
│  ├── Complex multi-step work → Claude sub-agents            │
│  └── Simple/bulk tasks → Ollama workers (this skill)        │
│                              ↓                              │
│                     [Mandatory Review]                      │
│                              ↓                              │
│                         User sees it                        │
└─────────────────────────────────────────────────────────────┘
```

**Why this matters:**
- Local models are free and fast, but can hallucinate
- Cloud models (Kimi, GLM) are cheap and capable, but not Claude
- Claude stays in control, catches errors, adds judgment
- User never sees raw unreviewed output

## Installation

### Prerequisites

1. **Ollama** installed and running:
   ```bash
   # macOS
   brew install ollama
   ollama serve
   ```

2. **Models pulled:**
   ```bash
   # Local (runs on your hardware)
   ollama pull llama3:8b      # 4.7GB, general purpose
   ollama pull phi3:mini      # 2.2GB, quick tasks
   
   # Cloud (requires ollama signin)
   ollama signin
   ollama pull kimi-k2.5:cloud   # Best quality, vision+thinking
   ollama pull glm-4.7:cloud     # Good for creative/coding
   ```

### As a Clawdbot Skill

```bash
# Via ClawdHub
clawdhub install ollama-worker

# Or manually copy from another Clawdbot instance
```

## Usage

### Basic Delegation

```bash
# Default model (kimi-k2.5:cloud)
python3 worker.py delegate --task "Summarize this article" --input "$(cat article.txt)"

# Specific model
python3 worker.py delegate --model llama3:8b --task "Generate 10 product names for a coffee brand"
```

### Agent Swarm Mode 🐝

The killer feature. Triggers multi-agent decomposition via prompt engineering:

```bash
python3 worker.py delegate --swarm --task "Design a complete authentication system for a mobile app"
```

What happens:
1. Kimi decomposes the task into specialized sub-tasks
2. Spawns named agents (Agent-1: Security Expert, Agent-2: UX Designer, etc.)
3. Each agent provides independent analysis
4. Synthesis Coordinator integrates findings
5. Output wrapped in orchestration markers

```bash
# Control agent count
python3 worker.py delegate --swarm --agents 5 --task "Competitive analysis of X vs Y vs Z"
```

**Great for:** architecture design, research, competitive analysis, complex decisions.

### Thinking Mode

Step-by-step reasoning (appears in stderr, clean answer in stdout):

```bash
python3 worker.py delegate --think --task "If a train leaves Chicago at 9am going 60mph..."
```

### Vision

Analyze images:

```bash
python3 worker.py delegate --image screenshot.png --task "What's wrong with this UI?"
python3 worker.py delegate --image receipt.jpg --task "Extract line items as JSON" --json
```

### JSON Output

Force structured output:

```bash
python3 worker.py delegate --json --task "Extract entities from: John Smith works at Acme Corp in NYC"
```

### Tool Calling

```bash
# tools.json defines available functions
python3 worker.py delegate --tools tools.json --task "What's the weather in Tokyo?"
```

## Model Selection Guide

| Model | Speed | Quality | Features | Cost | Best For |
|-------|-------|---------|----------|------|----------|
| `phi3:mini` | ⚡⚡⚡ | ⭐⭐ | basic | Free | Quick utilities, classification |
| `llama3:8b` | ⚡⚡ | ⭐⭐⭐ | basic | Free | Local general tasks |
| `glm-4.7:cloud` | ⚡⚡ | ⭐⭐⭐⭐ | tools | Cheap | Creative writing, coding |
| `kimi-k2.5:cloud` | ⚡ | ⭐⭐⭐⭐⭐ | vision, tools, thinking | Cheap | Default — highest quality |

**Cloud models require `:cloud` suffix** when pulling.

## When to Delegate

### Good Candidates ✅

- **Summarization** — long docs, articles, transcripts
- **Draft generation** — variations, boilerplate, first passes
- **Data extraction** — parse structure from text
- **Bulk classification** — tag/categorize many items
- **Image analysis** — describe, OCR, visual Q&A
- **Math/logic** — with thinking mode for verification
- **Code scaffolding** — boilerplate, tests, utilities

### Keep for Claude ❌

- Multi-step tool use chains
- Tasks requiring full conversation context
- Final user-facing responses
- Security-sensitive operations
- Anything where errors have real consequences

## Architecture Deep Dive

### The Orchestrator Pattern

This isn't just "call another model." It's a specific workflow:

1. **Identify** — Claude recognizes a delegatable task
2. **Delegate** — Clear instructions to Ollama worker
3. **Review** — Claude checks output for:
   - Hallucinations
   - Missing information
   - Logical errors
   - Tone/style issues
4. **Integrate** — Use the output, refine it, or redo if needed
5. **Deliver** — Only reviewed content reaches the user

### Why Mandatory QC?

Local/cloud models are good but not infallible:
- They hallucinate facts
- They miss nuance
- They can be confidently wrong
- They lack your conversation context

Claude catches these. The user trusts Claude, not the worker model.

### Logging

All delegations logged to `~/clawd/logs/ollama-delegations.jsonl`:

```json
{
  "timestamp": "2026-01-29T15:30:00",
  "model": "kimi-k2.5:cloud",
  "task_preview": "Summarize this article...",
  "tokens_in": 1500,
  "tokens_out": 400,
  "elapsed_seconds": 3.2,
  "thinking": true,
  "swarm": false
}
```

View stats:
```bash
python3 worker.py stats
```

## Configuration

Environment variables:

```bash
OLLAMA_HOST=http://localhost:11434  # Default Ollama endpoint
```

## Examples

### Research Assistant

```bash
# Swarm mode for multi-faceted research
python3 worker.py delegate --swarm \
  --task "Research the pros and cons of PostgreSQL vs MongoDB for a high-write IoT application"
```

### Document Processing Pipeline

```bash
# Extract structure from messy data
python3 worker.py delegate --json \
  --task "Extract all people, companies, and dates from this text" \
  --input "$(cat messy_notes.txt)"
```

### Code Review Helper

```bash
# Generate initial review, then Claude refines
python3 worker.py delegate --think \
  --task "Review this code for security issues and suggest improvements" \
  --input "$(cat pull_request.diff)"
```

### Visual Analysis

```bash
# Screenshot analysis
python3 worker.py delegate \
  --image app_screenshot.png \
  --task "List all UX issues you see and suggest fixes"
```

## Contributing

Issues and PRs welcome. The interesting work is in:
- Better swarm prompts for specific domains
- Additional output formats
- Integration patterns with other tools

## License

MIT

---

*Built for [Clawdbot](https://github.com/clawdbot/clawdbot) — the AI agent framework.*

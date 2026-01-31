# Delegation Guide for Clawdbot Agents

> How to use Ollama workers effectively. Learn from Mordecai's approach.

## The Core Philosophy

**You are the orchestrator. Kimi is your worker.**

You (Claude) handle: judgment, context, relationships, quality control, final delivery.
Kimi handles: heavy lifting, research, drafting, analysis, bulk work.

```
User asks something
        ↓
  Is this delegatable?
        ↓
   ┌────┴────┐
   No       Yes
   ↓         ↓
Do it    Delegate to Kimi
yourself       ↓
         Review output
               ↓
         Fix/enhance if needed
               ↓
         Deliver to user
```

**The user trusts YOU, not Kimi. Never show unreviewed output.**

---

## When to Delegate

### ✅ DELEGATE These Tasks

| Task | Why | Example |
|------|-----|---------|
| **Research** | Kimi can synthesize info fast | "Research pros/cons of PostgreSQL vs MongoDB" |
| **Drafting** | First passes are cheap | "Draft an email declining this invitation" |
| **Summarization** | Bulk text processing | "Summarize this 50-page PDF" |
| **Data extraction** | Pattern matching at scale | "Extract all dates and names from this doc" |
| **Code scaffolding** | Boilerplate generation | "Generate a REST API skeleton for users CRUD" |
| **Analysis** | Multiple perspectives | "Analyze this business plan for weaknesses" |
| **Image analysis** | Vision tasks | "What's in this screenshot?" |
| **Brainstorming** | Generate options | "Give me 20 names for a coffee brand" |

### ❌ DON'T Delegate These

| Task | Why |
|------|-----|
| **Personal context needed** | Kimi doesn't know the user's history |
| **Judgment calls** | That's YOUR job as the trusted agent |
| **Multi-step tool chains** | You need to orchestrate, not delegate |
| **Security-sensitive ops** | Keep control of risky operations |
| **Final responses** | Always review before user sees it |
| **Quick factual lookups** | Just use web search yourself |
| **Tasks under 30 seconds** | Overhead isn't worth it |

---

## How to Delegate

### Basic Command

```bash
python3 ~/clawd/skills/ollama-worker/worker.py delegate \
  --task "Your clear instructions here" \
  --input "Optional context/content"
```

### With Specific Model

```bash
# Fast local model for simple tasks
python3 worker.py delegate --model phi3:mini --task "Classify this as positive/negative"

# High-quality cloud model for complex tasks (default)
python3 worker.py delegate --model kimi-k2.5:cloud --task "Analyze this architecture"
```

### Agent Swarm Mode 🐝

For complex multi-faceted tasks, use swarm mode. Kimi spawns multiple specialized agents:

```bash
python3 worker.py delegate --swarm \
  --task "Design a complete authentication system for a mobile app"
```

This triggers:
- Task decomposition into sub-tasks
- Named specialist agents (Security Expert, UX Designer, etc.)
- Independent analysis from each perspective
- Synthesis of findings

**Best for:** architecture, research, competitive analysis, complex decisions.

### Thinking Mode

For tasks requiring reasoning:

```bash
python3 worker.py delegate --think \
  --task "If a train leaves Chicago at 9am going 60mph..."
```

### Vision

For image analysis:

```bash
python3 worker.py delegate \
  --image /path/to/screenshot.png \
  --task "List all UX issues in this interface"
```

### JSON Output

For structured data:

```bash
python3 worker.py delegate --json \
  --task "Extract entities from: John Smith works at Acme Corp"
```

---

## The Mandatory QC Pattern

**NEVER deliver raw Kimi output to the user.**

After every delegation:

1. **Read the output** — Does it answer the question?
2. **Check for hallucinations** — Any made-up facts?
3. **Verify logic** — Does the reasoning hold?
4. **Add context** — What does Kimi not know that you do?
5. **Adjust tone** — Match the user's communication style
6. **Integrate** — Combine with your own judgment

### Example Workflow

```
User: "Can you research whether I should use Kubernetes for my small side project?"

You (thinking): This is a research task. Delegate it, then add judgment.

1. Delegate:
   python3 worker.py delegate --task "Research pros and cons of Kubernetes 
   for small side projects (1-2 developers, moderate traffic)"

2. Kimi returns: [detailed analysis]

3. You review: 
   - Facts look correct ✓
   - Misses context that user is solo dev ✗
   - Tone is too formal ✗

4. You deliver:
   "Based on my research, Kubernetes is probably overkill for your side project. 
   Here's why: [your synthesis + Kimi's points, rewritten in casual tone]
   
   For a solo dev, I'd suggest Docker Compose or even just a simple VPS.
   Want me to outline a simpler setup?"
```

---

## Integration with AGENTS.md

Add this to your workspace's AGENTS.md:

```markdown
## Delegation

When tasks are substantial (research, analysis, drafting, critique), delegate to Kimi:

\`\`\`bash
python3 ~/clawd/skills/ollama-worker/worker.py delegate --task "<task>"
\`\`\`

Use `--swarm` for complex multi-faceted tasks.
Use `--think` for reasoning tasks.
Use `--image` for vision tasks.

**Rules:**
- Always QC before delivering to user
- Add your own context and judgment
- Never show raw unreviewed output
```

---

## Real Examples from Mordecai

### Research Delegation

```bash
# User asked about tech-aesthetic apparel market
python3 worker.py delegate \
  --task "Research the competitive landscape for tech-aesthetic apparel on Etsy. 
  What similar shops exist? What price points work? What keywords drive traffic?"
```

Then I reviewed, added context about their specific shop, and delivered insights.

### Creative War Room (Swarm)

```bash
# Multiple specialists for Etsy shop strategy
python3 worker.py delegate --swarm \
  --task "Analyze this Etsy shop and provide: market positioning, 
  customer psychology insights, marketing copy suggestions, and critique"
```

Got perspectives from Researcher, Analyst, Writer, and Critic agents.

### Draft Generation

```bash
# Generate options, then curate
python3 worker.py delegate \
  --task "Write 5 different taglines for a tech-nature fusion apparel brand 
  called Kyroku. Target: software engineers who love hiking."
```

Then I picked the best ones and refined them.

---

## Model Selection Cheat Sheet

| Situation | Model | Why |
|-----------|-------|-----|
| Quick classification | `phi3:mini` | Fast, free, good enough |
| General tasks | `llama3:8b` | Balanced local option |
| Complex analysis | `kimi-k2.5:cloud` | Best quality, use by default |
| Creative writing | `glm-4.7:cloud` | Good at prose |
| Image analysis | `kimi-k2.5:cloud` | Only one with vision |
| Cost-sensitive bulk | `phi3:mini` | Free and fast |

---

## Common Pitfalls

### ❌ Over-delegating
Don't delegate everything. Quick questions, personal context, judgment calls — do those yourself.

### ❌ Under-reviewing
"Kimi said it so it must be right" — NO. Always verify. Kimi hallucinates.

### ❌ Losing your voice
Don't just pass through Kimi's words. Rewrite in your style, add your perspective.

### ❌ Missing context
Kimi doesn't know the user's history. Add relevant context they need.

### ❌ Wrong model for the job
Don't use `kimi-k2.5:cloud` for simple yes/no classification. Don't use `phi3:mini` for nuanced analysis.

---

## Summary

1. **You're the orchestrator** — Kimi works for you, not the user
2. **Delegate heavy lifting** — Research, drafts, analysis, bulk work
3. **Keep judgment for yourself** — Context, relationships, final decisions
4. **Always QC** — Never show unreviewed output
5. **Use swarm for complexity** — Multiple perspectives beat single analysis
6. **Match model to task** — Don't overthink it, but don't waste resources

---

*Built for [Clawdbot](https://github.com/clawdbot/clawdbot) agents who want to scale their capabilities.*

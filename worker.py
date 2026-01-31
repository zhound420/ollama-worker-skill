#!/usr/bin/env python3
"""
Ollama Worker - Delegate tasks to Ollama models with full feature support

Usage:
    worker.py models                          # List available models
    worker.py delegate --task "..."           # Delegate (uses kimi-k2.5:cloud by default)
    worker.py delegate --swarm --task "..."   # Agent Swarm mode (decomposes into sub-agents)
    worker.py delegate --think --task "..."   # Enable thinking/reasoning mode
    worker.py delegate --image path.jpg ...   # With image input (vision)
    worker.py stats                           # Show delegation stats
"""

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LOG_FILE = Path.home() / "clawd" / "logs" / "ollama-delegations.jsonl"
DEFAULT_MODEL = "kimi-k2.5:cloud"

# The magic system prompt that triggers agent swarm behavior
SWARM_SYSTEM_PROMPT = """You are an AI with Agent Swarm capabilities. For complex tasks, you MUST:

1. **Decompose**: Break the task into distinct sub-tasks that can be handled by specialized agents
2. **Spawn Agents**: Create named agents (Agent-1, Agent-2, etc.) each with a specific role/expertise
3. **Execute**: Have each agent complete their analysis/work independently  
4. **Synthesize**: Coordinate findings from all agents into a unified response

Format your response as:
- [ORCHESTRATION PROTOCOL INITIATED]
- Agent sections with clear headers (### Agent-N: Role)
- Each agent provides their specialized analysis
- Synthesis Coordinator section that integrates all findings
- [ORCHESTRATION COMPLETE - All agents terminated]

Be thorough. Each agent should be an expert in their domain. The synthesis should add value beyond just combining outputs."""


def list_models():
    """List available Ollama models."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        print("Installed models:")
        for model in data.get("models", []):
            name = model["name"]
            size = model.get("size", 0)
            if size and size > 0:
                size_str = f"{size / 1e9:.1f}GB"
            else:
                size_str = "cloud"
            print(f"  • {name} ({size_str})")
        
        print(f"\nDefault: {DEFAULT_MODEL}")
        print("\nTo add cloud models: ollama pull <model>:cloud")
        print("Available: kimi-k2.5, glm-4.7, deepseek-v3.1, qwen3-vl, devstral-2")
            
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Is it running?")
        print("Start with: ollama serve")
        sys.exit(1)


def encode_image(image_path: str) -> str:
    """Encode an image file to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def delegate(
    model: str,
    task: str,
    input_text: str = None,
    system: str = None,
    think: bool = False,
    swarm: bool = False,
    image: str = None,
    tools_file: str = None,
    json_output: bool = False,
    agents: int = None,
):
    """Delegate a task to an Ollama model."""
    
    # Use chat API for full feature support
    messages = []
    
    # Determine system prompt
    if swarm:
        # Agent swarm mode - use the magic prompt
        swarm_prompt = SWARM_SYSTEM_PROMPT
        if agents:
            swarm_prompt += f"\n\nSpawn exactly {agents} specialized agents for this task."
        if system:
            swarm_prompt += f"\n\nAdditional context: {system}"
        messages.append({"role": "system", "content": swarm_prompt})
    elif system:
        messages.append({"role": "system", "content": system})
    
    # Build user message
    user_content = task
    if input_text:
        user_content = f"{task}\n\n---\n\n{input_text}"
    
    user_msg = {"role": "user", "content": user_content}
    
    # Add image if provided
    if image:
        if os.path.exists(image):
            user_msg["images"] = [encode_image(image)]
        else:
            print(f"Warning: Image file not found: {image}", file=sys.stderr)
    
    messages.append(user_msg)
    
    # Build request payload
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    
    # Enable thinking mode (auto-enable for swarm)
    if think or swarm:
        payload["think"] = True
    
    # Add tools if provided
    if tools_file and os.path.exists(tools_file):
        with open(tools_file) as f:
            payload["tools"] = json.load(f)
    
    # Request JSON output
    if json_output:
        payload["format"] = "json"
    
    try:
        start = datetime.now()
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=600 if swarm else 300  # Longer timeout for swarm
        )
        resp.raise_for_status()
        result = resp.json()
        elapsed = (datetime.now() - start).total_seconds()
        
        message = result.get("message", {})
        response_text = message.get("content", "")
        thinking_text = message.get("thinking", "")
        tool_calls = message.get("tool_calls", [])
        
        # Log the delegation
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "task_preview": task[:100],
            "input_chars": len(input_text) if input_text else 0,
            "output_chars": len(response_text),
            "thinking": bool(thinking_text),
            "swarm": swarm,
            "tool_calls": len(tool_calls),
            "has_image": bool(image),
            "prompt_eval_count": result.get("prompt_eval_count", 0),
            "eval_count": result.get("eval_count", 0),
            "elapsed_seconds": round(elapsed, 2),
        }
        
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Output thinking if present
        if thinking_text:
            print("=== THINKING ===", file=sys.stderr)
            print(thinking_text, file=sys.stderr)
            print("=== END THINKING ===\n", file=sys.stderr)
        
        # Output tool calls if present
        if tool_calls:
            print("=== TOOL CALLS ===", file=sys.stderr)
            print(json.dumps(tool_calls, indent=2), file=sys.stderr)
            print("=== END TOOL CALLS ===\n", file=sys.stderr)
        
        # Output the response
        print(response_text)
        
        # Stats to stderr
        print(f"\n--- Worker Stats ---", file=sys.stderr)
        print(f"Model: {model}", file=sys.stderr)
        print(f"Tokens: {result.get('prompt_eval_count', '?')} in, {result.get('eval_count', '?')} out", file=sys.stderr)
        print(f"Time: {elapsed:.1f}s", file=sys.stderr)
        if swarm:
            print(f"Mode: 🐝 Agent Swarm", file=sys.stderr)
        elif think:
            print(f"Thinking: enabled", file=sys.stderr)
        if image:
            print(f"Vision: {image}", file=sys.stderr)
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Is it running?", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def show_stats():
    """Show delegation statistics."""
    if not LOG_FILE.exists():
        print("No delegations logged yet.")
        return
    
    entries = []
    with open(LOG_FILE) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    
    if not entries:
        print("No delegations logged yet.")
        return
    
    # Aggregate by model
    by_model = {}
    total_thinking = 0
    total_vision = 0
    total_tools = 0
    total_swarm = 0
    
    for e in entries:
        model = e.get("model", "unknown")
        if model not in by_model:
            by_model[model] = {"count": 0, "tokens_in": 0, "tokens_out": 0, "time": 0}
        by_model[model]["count"] += 1
        by_model[model]["tokens_in"] += e.get("prompt_eval_count", 0)
        by_model[model]["tokens_out"] += e.get("eval_count", 0)
        by_model[model]["time"] += e.get("elapsed_seconds", 0)
        
        if e.get("thinking"):
            total_thinking += 1
        if e.get("has_image"):
            total_vision += 1
        if e.get("tool_calls", 0) > 0:
            total_tools += 1
        if e.get("swarm"):
            total_swarm += 1
    
    print(f"Total delegations: {len(entries)}")
    print(f"  With thinking: {total_thinking}")
    print(f"  With swarm: {total_swarm}")
    print(f"  With vision: {total_vision}")
    print(f"  With tool calls: {total_tools}")
    
    print(f"\nBy model:")
    for model, stats in sorted(by_model.items(), key=lambda x: -x[1]["count"]):
        print(f"  {model}:")
        print(f"    Count: {stats['count']}")
        print(f"    Tokens: {stats['tokens_in']:,} in, {stats['tokens_out']:,} out")
        print(f"    Time: {stats['time']:.1f}s total")


def main():
    parser = argparse.ArgumentParser(description="Ollama Worker - Delegate tasks to Ollama models")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # models command
    subparsers.add_parser("models", help="List available models")
    
    # delegate command
    delegate_parser = subparsers.add_parser("delegate", help="Delegate a task")
    delegate_parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    delegate_parser.add_argument("--task", "-t", required=True, help="Task description/prompt")
    delegate_parser.add_argument("--input", "-i", help="Input text to process")
    delegate_parser.add_argument("--system", "-s", help="System prompt")
    delegate_parser.add_argument("--think", action="store_true", help="Enable thinking/reasoning mode")
    delegate_parser.add_argument("--swarm", action="store_true", help="Enable Agent Swarm mode (auto-decompose into sub-agents)")
    delegate_parser.add_argument("--agents", type=int, help="Number of agents to spawn (with --swarm)")
    delegate_parser.add_argument("--image", help="Path to image file (for vision)")
    delegate_parser.add_argument("--tools", help="Path to tools JSON file")
    delegate_parser.add_argument("--json", action="store_true", help="Request JSON output")
    
    # stats command
    subparsers.add_parser("stats", help="Show delegation statistics")
    
    args = parser.parse_args()
    
    if args.command == "models":
        list_models()
    elif args.command == "delegate":
        delegate(
            args.model,
            args.task,
            args.input,
            args.system,
            args.think,
            getattr(args, 'swarm', False),
            args.image,
            args.tools,
            args.json,
            getattr(args, 'agents', None),
        )
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

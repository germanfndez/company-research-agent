# Company Research Agent

A custom AI agent loop that autonomously researches a company using sequential skills.
Built as a technical assessment to demonstrate agent architecture fundamentals.

## Architecture

```
main.py        → entry point
src/
  state.py     → AgentState + Execution (Pydantic) — single source of truth
  skills.py    → 3 mock tools: search_company, get_financials, write_summary
  hooks.py     → pre/post hooks: logging, human approval, auditing
  llm.py       → mock LLM brain: call_llm() + mock_agent_decision()
  agent.py     → the while loop: observe → decide → act → update
```

## Agent Loop

```
User prompt
    │
    ▼
run_agent(prompt, pre_hooks, post_hooks, permissions, max_turns, max_retries)
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  while not state.is_finished:                                       │
│                                                                     │
│  0. max_turns guard          ← circuit breaker, hard stop          │
│         │ exceeded → records Execution(error) → is_finished = True │
│         ▼                                                           │
│  1. decision = mock_agent_decision(state)   ← LLM decides          │
│         │ reads full state + executions history                     │
│         │ returns ToolCall { tool, args }                           │
│         ▼                                                           │
│  2. tool == "FINISH"?  ──YES──► is_finished = True, break          │
│         │ NO                                                        │
│         ▼                                                           │
│  3. pre_hooks(tool, state, permissions)     ← logging / approval   │
│         │ PermissionError → records Execution(error), skips skill  │
│         │ (LLM sees the block next turn and decides what to do)    │
│         ▼                                                           │
│  4. skill(**args)  [retry up to max_retries]                        │
│         │ success → records Execution(result)                      │
│         │ all retries failed → records Execution(error), continues │
│         │ (LLM sees the failure next turn and decides what to do)  │
│         ▼                                                           │
│  5. post_hooks(tool, result, state)         ← audit / notify       │
│         ▼                                                           │
│     back to top                                                     │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
return state.final_summary
```

### Permission system

```python
permissions = {
    "search_company": "allow",   # runs automatically
    "get_financials": "ask",     # requires human confirmation
    "write_summary":  "allow",   # runs automatically
}
```

### Failure recovery

When a skill fails all retries or is blocked by a permission, the agent does **not** stop. The error is recorded in `state.executions` and the loop continues — `mock_agent_decision` reads the full transcript on the next turn and decides the next step.

Example: `get_financials` fails → LLM sees it in the transcript → calls `write_summary` with the partial data available → report is generated with `N/A` for missing financials.

## Setup

```bash
pip install -r requirements.txt
```

> Requires Python 3.10+

## Run

```bash
python main.py
```

## Swapping the mock LLM for a real model

Only `call_llm()` in `src/llm.py` needs to change:

```python
def call_llm(prompt: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

The agent loop, skills, hooks, and state are untouched.

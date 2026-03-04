# Company Research Agent

A custom AI agent loop that autonomously researches a company using sequential skills.
Built as a technical assessment to demonstrate agent architecture fundamentals.

## Architecture

```
state.py   → AgentState (Pydantic) — single source of truth
skills.py  → 3 mock tools: search_company, get_financials, write_summary
hooks.py   → pre/post hooks: logging, human approval, auditing
llm.py     → mock LLM brain: call_llm() + mock_agent_decision()
agent.py   → the while loop: observe → decide → act → update
main.py    → entry point
```

### Agent Loop

```
┌──────────────────────────────────────────────────────┐
│  while not state.is_finished:                        │
│    decision = mock_agent_decision(state)             │  ← LLM decides
│    run pre_hooks(tool, state)                        │  ← logging / approval
│    result = execute_skill(decision.tool, args)       │  ← skill runs
│    state.update(result)                              │  ← state updated
│    run post_hooks(tool, result, state)               │  ← audit / notify
└──────────────────────────────────────────────────────┘
```

## Setup

```bash
pip install pydantic
```

> Requires Python 3.10+

## Run

```bash
# Default mode (no hooks)
python main.py
```

To enable **human-in-the-loop** mode, edit `main.py` and change `run_default()` to `run_with_hooks()`.

## Swapping the mock LLM for a real model

Only `call_llm()` in `llm.py` needs to change:

```python
# Replace the mock body with:
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
)
return response.choices[0].message.content
```

The agent loop, skills, hooks, and state are untouched.

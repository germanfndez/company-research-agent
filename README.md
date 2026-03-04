# Company Research Agent

A custom AI agent loop that autonomously researches a company using sequential skills.
Built as a technical assessment to demonstrate agent architecture fundamentals.

## Architecture

```
main.py        → entry point
src/
  state.py     → AgentState (Pydantic) — single source of truth
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
run_agent(prompt, pre_hooks, post_hooks, permissions)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  while not state.is_finished:                                   │
│                                                                 │
│  1. decision = mock_agent_decision(state)   ← LLM decides      │
│          │ returns ToolCall { tool, args }                      │
│          ▼                                                      │
│  2. pre_hooks(tool, state, permissions)     ← logging / OK?    │
│          │ raises PermissionError → stop                        │
│          ▼                                                      │
│  3. result = skill(**args)                  ← executes tool     │
│          │ retry up to max_retries on failure                   │
│          ▼                                                      │
│  4. state.field = result                    ← updates state     │
│          ▼                                                      │
│  5. post_hooks(tool, result, state)         ← audit / notify   │
│          ▼                                                      │
│     FINISH? ──YES──► return state.final_summary                 │
│          │                                                      │
│          NO (next turn, max_turns guard)                        │
└─────────────────────────────────────────────────────────────────┘
```

### Skills executed in order

```
search_company(query)
    → state.company_info = { name, location, industry, founded }

get_financials(company_name)
    → state.financial_info = { revenue, employees, funding_stage }

write_summary(company_data, financial_data)
    → state.final_summary = "Company Report: ..."
```

### Permission system

```python
permissions = {
    "search_company": "allow",   # runs automatically
    "get_financials": "ask",     # requires human confirmation
    "write_summary":  "allow",   # runs automatically
}
```

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

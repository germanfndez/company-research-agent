# Company Research Agent — LLM Context

## What this project is

A custom AI agent loop built in Python. Given a user prompt, the agent autonomously
calls a sequence of skills (tools) to research a company and produce a final report.

No real LLM API is used — the decision logic is mocked to evaluate pure agent architecture.

## Architecture

```
state.py    AgentState (Pydantic) — single source of truth for the loop
skills.py   3 mock tools: search_company, get_financials, write_summary
hooks.py    Pre/post hook system with typed permissions per skill
llm.py      call_llm() API boundary + mock_agent_decision() brain
agent.py    run_agent() — the while loop orchestrator
main.py     Entry point
```

## Agent loop flow

```
while not state.is_finished:
    decision = mock_agent_decision(state)   # LLM decides: {tool, args}
    run pre_hooks(tool, state, permissions) # logging, human approval, etc.
    result = skill(**args)                  # execute with retry (max_retries)
    state.<field> = result                  # update state
    run post_hooks(tool, result, state)     # audit, notifications, etc.
    turn += 1                               # guard against infinite loops (max_turns)
```

## Key types (hooks.py)

```python
Permission  = Literal["allow", "ask"]
Permissions = dict[str, Permission]        # per-skill human approval config
PreHook     = Callable[[str, AgentState, Permissions], None]
PostHook    = Callable[[str, Any, AgentState], None]
ToolCall    = TypedDict(tool=str, args=dict)  # what mock_agent_decision returns
```

## run_agent() signature

```python
run_agent(
    prompt: str,
    max_turns: int = 10,       # stops infinite loops
    max_retries: int = 3,      # retries failed skills before giving up
    pre_hooks: list[PreHook],
    post_hooks: list[PostHook],
    permissions: Permissions,  # which skills require human confirmation
) -> str | None
```

## Swapping mock LLM for a real model

Only `call_llm()` in `llm.py` needs to change. The loop, skills, hooks, and state are untouched:

```python
def call_llm(prompt: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

## Available skills

### `.agents/skills/python-design-patterns`
Python design principles (KISS, SRP, Separation of Concerns, Composition over Inheritance).
Apply when making architecture decisions or evaluating abstractions in this codebase.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

from .hooks import Permissions, PostHook, PreHook
from .llm import mock_agent_decision
from .skills import get_financials, search_company, write_summary
from .state import AgentState, Execution


def run_agent(
    prompt: str,
    max_turns: int = 10,
    max_retries: int = 3,
    pre_hooks: list[PreHook] | None = None,
    post_hooks: list[PostHook] | None = None,
    permissions: Permissions | None = None,
) -> str | None:
    pre_hooks = pre_hooks or []
    post_hooks = post_hooks or []
    permissions = permissions or {}

    state = AgentState(user_prompt=prompt)
    print(f"\n[agent] Starting. Task: '{prompt}'\n")

    turn = 0

    while not state.is_finished:
        if turn >= max_turns:
            print(f"[agent] Max turns ({max_turns}) reached without finishing.")
            state.errors.append(f"Max turns exceeded: {max_turns}")
            state.is_finished = True
            break

        turn += 1
        decision = mock_agent_decision(state)

        tool_name = decision["tool"]
        tool_args = decision["args"]

        print(f"[agent] Turn {turn}/{max_turns} → tool='{tool_name}'")

        if tool_name == "FINISH":
            state.is_finished = True
            break

        try:
            for hook in pre_hooks:
                hook(tool_name, state, permissions)
        except PermissionError as e:
            print(f"[agent] Action blocked: {e}")
            state.errors.append(str(e))
            state.is_finished = True
            break

        for attempt in range(max_retries):
            try:
                result = None

                if tool_name == "search_company":
                    state.company_info = search_company(**tool_args)
                    result = state.company_info

                elif tool_name == "get_financials":
                    state.financial_info = get_financials(**tool_args)
                    result = state.financial_info

                elif tool_name == "write_summary":
                    state.final_summary = write_summary(**tool_args)
                    result = state.final_summary

                state.executions.append(Execution(turn=turn, tool=tool_name, args=tool_args, result=result))

                for hook in post_hooks:
                    hook(tool_name, result, state)

                break  # skill succeeded — exit retry loop

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[agent] '{tool_name}' failed (attempt {attempt + 1}/{max_retries}), retrying...")
                else:
                    print(f"[agent] '{tool_name}' failed after {max_retries} attempts. Recording error, letting LLM decide next step.")
                    state.executions.append(Execution(turn=turn, tool=tool_name, args=tool_args, error=str(e)))
                    state.errors.append(str(e))

    print("\n[agent] Loop finished.")
    return state.final_summary

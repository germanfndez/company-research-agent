from hooks import Permissions, PostHook, PreHook
from llm import mock_agent_decision
from skills import get_financials, search_company, write_summary
from state import AgentState


def run_agent(
    prompt: str,
    pre_hooks: list[PreHook] = [],
    post_hooks: list[PostHook] = [],
    permissions: Permissions = {},
) -> str | None:

    state = AgentState(user_prompt=prompt)
    print(f"\n[agent] Starting. Task: '{prompt}'\n")

    while not state.is_finished:
        decision = mock_agent_decision(state)

        tool_name = decision["tool"]
        tool_args = decision["args"]

        print(f"[agent] LLM decision → tool='{tool_name}', args={tool_args}")

        if tool_name == "FINISH":
            state.is_finished = True
            break

        for hook in pre_hooks:
            hook(tool_name, state, permissions)

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

            for hook in post_hooks:
                hook(tool_name, result, state)

        except PermissionError as e:
            # A pre-hook (e.g. human_approval_pre_hook) denied the action
            print(f"[agent] Action blocked: {e}")
            state.errors.append(str(e))
            state.is_finished = True

        except Exception as e:
            # Unexpected skill failure — log and stop gracefully
            print(f"[agent] Skill '{tool_name}' failed: {e}")
            state.errors.append(str(e))
            state.is_finished = True

    print("\n[agent] Loop finished.")
    return state.final_summary

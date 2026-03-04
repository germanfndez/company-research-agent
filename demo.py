"""
Demo: Company Research Agent — Use Cases

Run with: python demo.py
"""

from src.agent import run_agent
from src.hooks import Permissions, audit_post_hook, logging_pre_hook
import src.agent as agent_mod


def divider(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ─────────────────────────────────────────────
# Case 1: Happy path — everything works
# ─────────────────────────────────────────────
def case_happy_path():
    divider("CASE 1 — Happy path (all skills succeed)")

    result = run_agent(
        prompt="Find information about a tech company in Berlin",
        pre_hooks=[logging_pre_hook],
        post_hooks=[audit_post_hook],
        permissions={
            "search_company": "allow",
            "get_financials":  "allow",
            "write_summary":   "allow",
        },
    )

    print("\n[result]", result)


# ─────────────────────────────────────────────
# Case 2: Failure recovery — get_financials fails
# ─────────────────────────────────────────────
def case_failure_recovery():
    divider("CASE 2 — Failure recovery (get_financials fails, agent recovers)")

    # Simulate a broken financial API
    original = agent_mod.get_financials
    agent_mod.get_financials = lambda **kw: (_ for _ in ()).throw(RuntimeError("Financial API unavailable"))

    result = run_agent(
        prompt="Find information about a tech company in Berlin",
        pre_hooks=[logging_pre_hook],
        post_hooks=[audit_post_hook],
        max_retries=2,
        permissions={
            "search_company": "allow",
            "get_financials":  "allow",
            "write_summary":   "allow",
        },
    )

    agent_mod.get_financials = original  # restore
    print("\n[result]", result)


# ─────────────────────────────────────────────
# Case 3: Permission denied — human blocks get_financials
# ─────────────────────────────────────────────
def case_permission_denied():
    divider("CASE 3 — Permission denied (human blocks get_financials, agent recovers)")

    def always_deny(action: str, state, permissions: Permissions) -> None:
        if action == "get_financials":
            raise PermissionError(f"'{action}' denied by user")

    result = run_agent(
        prompt="Find information about a tech company in Berlin",
        pre_hooks=[logging_pre_hook, always_deny],
        post_hooks=[audit_post_hook],
        permissions={
            "search_company": "allow",
            "get_financials":  "ask",
            "write_summary":   "allow",
        },
    )

    print("\n[result]", result)


# ─────────────────────────────────────────────
# Case 4: Max turns — agent hits the loop limit
# ─────────────────────────────────────────────
def case_max_turns():
    divider("CASE 4 — Max turns guard (loop hits the limit and stops)")

    # Simulate a skill that always fails so the agent loops
    original = agent_mod.get_financials
    agent_mod.get_financials = lambda **kw: (_ for _ in ()).throw(RuntimeError("Always fails"))

    # Also block write_summary recovery so the agent keeps trying
    original_write = agent_mod.write_summary
    agent_mod.write_summary = lambda **kw: (_ for _ in ()).throw(RuntimeError("Also fails"))

    result = run_agent(
        prompt="Find information about a tech company in Berlin",
        pre_hooks=[logging_pre_hook],
        max_retries=1,
        max_turns=4,
        permissions={
            "search_company": "allow",
            "get_financials":  "allow",
            "write_summary":   "allow",
        },
    )

    agent_mod.get_financials = original
    agent_mod.write_summary = original_write
    print("\n[result]", result)


if __name__ == "__main__":
    case_happy_path()
    case_failure_recovery()
    case_permission_denied()
    case_max_turns()

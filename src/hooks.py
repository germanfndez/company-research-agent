from typing import Any, Callable, Literal
from .state import AgentState

# A skill can either run automatically or require human confirmation
Permission = Literal["allow", "ask"]
Permissions = dict[str, Permission]

# Type aliases
PreHook  = Callable[[str, AgentState, Permissions], None]
PostHook = Callable[[str, Any, AgentState], None]


def logging_pre_hook(action: str, state: AgentState, permissions: Permissions) -> None:
    print(f"[pre-hook]  → about to execute '{action}'")


def human_approval_pre_hook(action: str, state: AgentState, permissions: Permissions) -> None:
    # If the skill is explicitly allowed (or absent from permissions), skip the prompt
    if permissions.get(action, "allow") == "allow":
        return

    response = input(f"[human] Allow '{action}'? (y/n): ").strip().lower()
    if response != "y":
        raise PermissionError(f"Action '{action}' was denied by the user.")


def audit_post_hook(action: str, result: Any, state: AgentState) -> None:
    print(f"[post-hook] ✓ '{action}' completed → {result}")

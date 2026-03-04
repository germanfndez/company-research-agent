from agent import run_agent
from hooks import Permission, audit_post_hook, human_approval_pre_hook, logging_pre_hook

if __name__ == "__main__":
    permissions: dict[str, Permission] = {
        "search_company": "allow",  # runs automatically
        "get_financials": "ask",    # requires human confirmation
        "write_summary":  "allow",  # runs automatically
    }

    result = run_agent(
        prompt="Find information about a tech company in Berlin",
        pre_hooks=[logging_pre_hook, human_approval_pre_hook],
        post_hooks=[audit_post_hook],
        permissions=permissions,
    )

    print("\n--- Final Output ---")
    print(result)

from agent import run_agent
from hooks import Permissions, audit_post_hook, human_approval_pre_hook, logging_pre_hook

if __name__ == "__main__":
    permissions: Permissions = {
        "search_company": "allow", 
        "get_financials": "ask", 
        "write_summary":  "allow", 
    }

    result = run_agent(
        prompt="Find information about a tech company in Berlin",
        pre_hooks=[logging_pre_hook, human_approval_pre_hook],
        post_hooks=[audit_post_hook],
        permissions=permissions,
        max_retries=3,
        max_turns=10,
    )

    print("\n--- Final Output ---")
    print(result)

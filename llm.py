from typing import TypedDict
from state import AgentState

class ToolCall(TypedDict):
    """
    Represents the LLM's decision: which tool to run and with what arguments.

    A real LLM (e.g. GPT-4 with function_calling) returns this exact structure.
    Our mock builds it manually from the state.
    """

    tool: str  
    args: dict


def call_llm(prompt: str) -> str:
    """
    Simulates a call to an LLM API.

    To switch to a real model, replace the body with:

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    The mock inspects the serialized state embedded in the prompt
    and applies simple rule-based logic to pick the next tool.
    """
    if '"company_info":null' in prompt:
        return "search_company"
    if '"financial_info":null' in prompt:
        return "get_financials"
    if '"final_summary":null' in prompt:
        return "write_summary"
        
    return "FINISH"


def mock_agent_decision(state: AgentState) -> ToolCall:
    """
    Builds a prompt from the current state and asks the LLM what to do next.
    Returns a ToolCall with the chosen tool and the arguments to pass it.

    In production, the LLM would reason over the full prompt and return
    both the tool name and arguments — we assemble args manually here
    because our mock only returns the tool name.
    """
    # Serialize state to JSON so the LLM can "read" it
    prompt = (
        f"User task: {state.user_prompt}\n"
        f"Current state: {state.model_dump_json()}\n"
        f"Available tools: search_company, get_financials, write_summary, FINISH\n"
        f"What tool should I call next?"
    )

    tool_name = call_llm(prompt)

    # Build the arguments the LLM "decided" to pass to each tool.
    # A real LLM with function_calling returns these directly in the API response.
    args: dict = {}
    if tool_name == "search_company":
        args = {"query": state.user_prompt}
    elif tool_name == "get_financials" and state.company_info:
        args = {"company_name": state.company_info["name"]}
    elif tool_name == "write_summary" and state.company_info and state.financial_info:
        args = {"company_data": state.company_info, "financial_data": state.financial_info}

    return ToolCall(tool=tool_name, args=args)

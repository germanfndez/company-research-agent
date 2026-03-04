from typing import Any, Optional
from pydantic import BaseModel

class Execution(BaseModel):
    turn: int
    tool: str
    args: dict
    result: Any = None
    error: str | None = None

class AgentState(BaseModel):
    user_prompt: str
    company_info: Optional[dict] = None
    financial_info: Optional[dict] = None
    final_summary: Optional[str] = None
    
    executions: list[Execution] = []
    is_finished: bool = False

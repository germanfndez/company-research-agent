from typing import Optional
from pydantic import BaseModel


class AgentState(BaseModel):
    user_prompt: str
    company_info: Optional[dict] = None
    financial_info: Optional[dict] = None
    final_summary: Optional[str] = None
    errors: list[str] = []
    is_finished: bool = False

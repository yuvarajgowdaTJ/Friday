from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from backend.core.planner import task_planner
from backend.core.agent import agent_instance

router = APIRouter(prefix="/api/agent", tags=["Agent"])

class AgentRunRequest(BaseModel):
    query: str
    auto_confirm: Optional[bool] = True

@router.post("/run")
def run_agent_task(request: AgentRunRequest):
    """Creates a plan and executes multi-step agent autonomous sequence."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    plan = task_planner.create_plan_for_query(request.query)
    result = agent_instance.execute_plan(plan, auto_confirm=request.auto_confirm)
    return result

@router.post("/plan")
def preview_agent_plan(request: AgentRunRequest):
    """Generates and previews a task plan without executing it."""
    plan = task_planner.create_plan_for_query(request.query)
    return plan.to_dict()

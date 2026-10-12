from backend.core.planner import task_planner
from backend.core.agent import agent_instance

def test_task_planner_creation():
    plan = task_planner.create_plan_for_query("Find PDF files and summarize")
    assert len(plan.steps) > 0
    assert plan.status == "PENDING"

def test_agent_execution():
    plan = task_planner.create_plan_for_query("Show system diagnostics")
    res = agent_instance.execute_plan(plan, auto_confirm=True)
    assert res["status"] in ["COMPLETED", "PARTIAL_SUCCESS"]
    assert res["steps_executed"] > 0

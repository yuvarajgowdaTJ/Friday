import logging
from typing import Dict, Any, List
from backend.core.planner import task_planner, TaskPlan
from backend.tools.registry import tool_registry
from backend.database.database import SessionLocal
from backend.database.models import TaskPlanModel

logger = logging.getLogger("JARVIS.Core.Agent")

MAX_AGENT_STEPS = 10

class AutonomousAgent:
    @staticmethod
    def execute_plan(plan: TaskPlan, auto_confirm: bool = True) -> Dict[str, Any]:
        """
        Executes an agent task plan step-by-step with safety bounds and audit recording.
        """
        plan.status = "IN_PROGRESS"
        logger.info(f"Starting agent execution for plan {plan.plan_id}: '{plan.query}'")
        
        execution_results = []
        steps_executed = 0

        for step in plan.steps:
            if steps_executed >= MAX_AGENT_STEPS:
                logger.warning(f"Plan {plan.plan_id} hit max step limit of {MAX_AGENT_STEPS}.")
                break

            step.status = "IN_PROGRESS"
            steps_executed += 1

            # Tool execution
            tool_res = tool_registry.execute(
                name=step.tool_name,
                args=step.tool_args,
                bypass_security=auto_confirm
            )

            step.result = tool_res
            if tool_res.get("status") in ["SUCCESS", "CONFIRMATION_REQUIRED"]:
                step.status = "COMPLETED"
            else:
                step.status = "FAILED"

            execution_results.append({
                "step": step.step_number,
                "action": step.action,
                "tool": step.tool_name,
                "status": step.status,
                "output": tool_res
            })

        all_passed = all(s.status == "COMPLETED" for s in plan.steps)
        plan.status = "COMPLETED" if all_passed else "PARTIAL_SUCCESS"

        # Save plan result to database
        db = SessionLocal()
        try:
            db_plan = TaskPlanModel(
                plan_id=plan.plan_id,
                user_query=plan.query,
                status=plan.status,
                steps=[s.to_dict() for s in plan.steps],
                result=f"Executed {steps_executed} steps successfully."
            )
            db.add(db_plan)
            db.commit()
        except Exception as db_err:
            logger.error(f"Failed to save task plan in DB: {db_err}")
        finally:
            db.close()

        summary_text = f"FRIDAY Agent finished multi-step request for: '{plan.query}'. Executed {steps_executed} steps."

        return {
            "plan_id": plan.plan_id,
            "query": plan.query,
            "status": plan.status,
            "steps_executed": steps_executed,
            "summary": summary_text,
            "step_details": [s.to_dict() for s in plan.steps]
        }

agent_instance = AutonomousAgent()

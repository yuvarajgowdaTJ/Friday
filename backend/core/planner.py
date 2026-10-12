import uuid
import logging
from typing import List, Dict, Any
from backend.core.brain import brain_instance

logger = logging.getLogger("JARVIS.Core.Planner")

class PlanStep:
    def __init__(self, step_number: int, action: str, tool_name: str, tool_args: Dict[str, Any], description: str):
        self.step_number = step_number
        self.action = action
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.description = description
        self.status = "PENDING" # PENDING, IN_PROGRESS, COMPLETED, FAILED
        self.result = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "description": self.description,
            "status": self.status,
            "result": self.result
        }

class TaskPlan:
    def __init__(self, query: str):
        self.plan_id = str(uuid.uuid4())[:8]
        self.query = query
        self.status = "PENDING"
        self.steps: List[PlanStep] = []

    def add_step(self, action: str, tool_name: str, tool_args: Dict[str, Any], description: str):
        step_num = len(self.steps) + 1
        step = PlanStep(step_num, action, tool_name, tool_args, description)
        self.steps.append(step)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "query": self.query,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps]
        }

class TaskPlanner:
    @staticmethod
    def create_plan_for_query(query: str) -> TaskPlan:
        """Generates a multi-step task plan for a user query."""
        plan = TaskPlan(query)
        q_lower = query.lower()

        if "internship" in q_lower or "compare" in q_lower or "search" in q_lower:
            plan.add_step("Search Web", "web_search", {"query": query}, "Execute web search for relevant opportunities/information.")
            plan.add_step("Summarize & Filter", "search_memories", {"query": "internship"}, "Check user preferences for filtering.")
            plan.add_step("Create Summary File", "create_file", {"path": "./data/internships_comparison.txt", "content": f"JARVIS Agent Plan Results for: {query}"}, "Save compiled analysis to text file.")
        elif "pdf" in q_lower or "file" in q_lower or "document" in q_lower or "find" in q_lower:
            pattern = ".pdf" if "pdf" in q_lower else "report"
            plan.add_step("Search Files", "search_files", {"pattern": pattern}, f"Search computer filesystem for '{pattern}'.")
            plan.add_step("System Diagnostics", "get_system_stats", {}, "Check hardware metrics.")
        else:
            plan.add_step("Web Intelligence", "web_search", {"query": query}, "Retrieve real-time data.")
            plan.add_step("Check System Stats", "get_system_stats", {}, "Collect current desktop state.")

        return plan

task_planner = TaskPlanner()

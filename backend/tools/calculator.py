import re
import math
import ast
import operator
import logging
from typing import Dict, Any, Union
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Tools.Calculator")

# Allowed operators for safe AST evaluation
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
}

class SafeEvaluator(ast.NodeVisitor):
    def visit(self, node: ast.AST) -> Union[int, float]:
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Constant(self, node: ast.Constant) -> Union[int, float]:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Union[int, float]:
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            operand = self.visit(node.operand)
            return ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")

    def visit_BinOp(self, node: ast.BinOp) -> Union[int, float]:
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            left = self.visit(node.left)
            right = self.visit(node.right)
            return ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type}")

    def visit_Call(self, node: ast.Call) -> Union[int, float]:
        if isinstance(node.func, ast.Name) and node.func.id in ALLOWED_FUNCTIONS:
            func = ALLOWED_FUNCTIONS[node.func.id]
            args = [self.visit(arg) for arg in node.args]
            return func(*args)
        raise ValueError(f"Unsupported function call: {getattr(node.func, 'id', str(node.func))}")

    def generic_visit(self, node: ast.AST):
        raise ValueError(f"Unsupported syntax: {type(node).__name__}")


def parse_natural_language_math(expression: str) -> str:
    """Converts natural language math phrases into standard arithmetic expressions."""
    text = expression.strip().lower()

    # Strip prefixes like "calculate", "compute", "what is", "please calculate", etc.
    text = re.sub(r'^(?:(?:friday|jarvis),?\s*)?(?:please\s+)?(?:calculate|compute|solve|evaluate)\s+', '', text)
    text = re.sub(r'^(?:(?:friday|jarvis),?\s*)?(?:please\s+)?what\s+is\s+', '', text)
    text = re.sub(r'^(?:tell\s+me\s+)?what\s+is\s+', '', text)
    text = re.sub(r'\?+$', '', text).strip()

    # Percentage: "15% of 800" or "15 percent of 800"
    perc_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s*of\s*(\d+(?:\.\d+)?)', text)
    if perc_match:
        p, val = perc_match.groups()
        return f"({p} / 100) * {val}"

    # Squared / Cubed: "27 squared", "5 cubed"
    sq_match = re.search(r'(\d+(?:\.\d+)?)\s*squared', text)
    if sq_match:
        return f"{sq_match.group(1)} ** 2"
    cb_match = re.search(r'(\d+(?:\.\d+)?)\s*cubed', text)
    if cb_match:
        return f"{cb_match.group(1)} ** 3"

    # Multiplied by / Times
    text = re.sub(r'\bmultiplied\s+by\b', '*', text)
    text = re.sub(r'\btimes\b', '*', text)
    text = re.sub(r'\bx\b', '*', text)

    # Divided by
    text = re.sub(r'\bdivided\s+by\b', '/', text)
    text = re.sub(r'\bover\b', '/', text)

    # Power: "2 to the power of 8", "2 power 8"
    text = re.sub(r'(\d+(?:\.\d+)?)\s*(?:to\s+the\s+power\s+(?:of\s+)?|power\s+)(\d+(?:\.\d+)?)', r'\1 ** \2', text)

    # Add / Plus
    add_match = re.search(r'add\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)', text)
    if add_match:
        return f"{add_match.group(1)} + {add_match.group(2)}"
    text = re.sub(r'\bplus\b', '+', text)
    text = re.sub(r'\band\b', '+', text)

    # Subtract / Minus: "subtract 30 from 100"
    sub_from = re.search(r'subtract\s+(\d+(?:\.\d+)?)\s+from\s+(\d+(?:\.\d+)?)', text)
    if sub_from:
        return f"{sub_from.group(2)} - {sub_from.group(1)}"
    text = re.sub(r'\bminus\b', '-', text)

    # Square root: "square root of 144"
    sqrt_match = re.search(r'square\s+root\s+(?:of\s+)?(\d+(?:\.\d+)?)', text)
    if sqrt_match:
        return f"sqrt({sqrt_match.group(1)})"

    # Clean non-math characters, keeping valid math tokens
    cleaned = re.sub(r'[^0-9\+\-\*\/\%\(\)\.\^\s_a-zA-Z]', '', text)
    cleaned = cleaned.replace('^', '**')
    return cleaned.strip()


@tool_registry.register(
    name="calculate",
    description="Safely calculates mathematical expressions or natural language math queries (e.g. '8 multiplied by 6', '125 divided by 5', '15% of 800', '27 squared').",
    parameters={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Mathematical expression or phrasing to evaluate"}
        },
        "required": ["expression"]
    }
)
def calculate(expression: str) -> Dict[str, Any]:
    """Evaluates a math expression safely using AST."""
    try:
        math_expr = parse_natural_language_math(expression)
        parsed = ast.parse(math_expr, mode='eval')
        evaluator = SafeEvaluator()
        result = evaluator.visit(parsed.body)

        # Format integer results without unnecessary decimal zeros
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 6)

        return {
            "status": "SUCCESS",
            "expression": expression,
            "parsed_expression": math_expr,
            "result": result,
            "speech_answer": f"{result}, sir."
        }
    except ZeroDivisionError:
        from backend.core.errors import ToolErrorCategory
        msg = "I can't divide by zero, sir. Division by zero is undefined."
        return {
            "status": "ERROR",
            "error_category": ToolErrorCategory.DIVISION_BY_ZERO.value,
            "expression": expression,
            "parsed_expression": math_expr,
            "result": "undefined",
            "error": "Division by zero is undefined.",
            "user_message": msg,
            "speech_answer": msg
        }
    except (ValueError, SyntaxError) as e:
        from backend.core.errors import ToolErrorCategory
        msg = "The provided calculation input is invalid or improperly formatted, sir."
        logger.error(f"Invalid math expression '{expression}': {e}", exc_info=True)
        return {
            "status": "ERROR",
            "error_category": ToolErrorCategory.INVALID_INPUT.value,
            "expression": expression,
            "error": str(e),
            "user_message": msg,
            "speech_answer": msg,
            "result": None
        }
    except Exception as e:
        from backend.core.errors import ToolErrorCategory
        msg = "I was unable to evaluate that calculation, sir."
        logger.error(f"Calculation failed for '{expression}': {e}", exc_info=True)
        return {
            "status": "ERROR",
            "error_category": ToolErrorCategory.CALCULATION_ERROR.value,
            "expression": expression,
            "error": str(e),
            "user_message": msg,
            "speech_answer": msg,
            "result": None
        }

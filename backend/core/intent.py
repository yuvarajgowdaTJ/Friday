"""
Intent Classifier module for FRIDAY.
Categorizes user natural language requests into structured intents and entities.
"""

import re
from enum import Enum
from typing import Dict, Any, Optional

class Intent(str, Enum):
    CONVERSATION = "conversation"
    SELF_QUERY = "self_query"
    RESEARCH = "research"
    CALCULATOR = "calculator"
    CREATIVE = "creative"
    COMPUTER_CONTROL = "computer_control"
    BROWSER = "browser"
    SCREENSHOT = "screenshot"
    SYSTEM = "system"
    MEMORY = "memory"
    MULTI_STEP_TASK = "multi_step_task"
    CLARIFICATION = "clarification"

    # Backward compatibility aliases
    GREETING = "conversation"
    SYSTEM_INFO = "system"
    OPEN_APPLICATION = "computer_control"
    CLOSE_APPLICATION = "computer_control"
    WEB_SEARCH = "research"
    WEB_RESEARCH = "research"
    MEMORY_SAVE = "memory"
    MEMORY_RECALL = "memory"
    MEMORY_FORGET = "memory"
    VISION = "screenshot"
    CODING = "multi_step_task"
    PLANNING = "multi_step_task"
    UNKNOWN = "clarification"

class IntentClassifier:
    """Deterministic, high-precision intent classifier for FRIDAY."""

    @staticmethod
    def classify(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raw = text.strip()
        t = raw.lower()

        # Semantic interpretation normalization (support shorthand 'u' -> 'you', 'ur' -> 'your')
        # Does NOT mutate the original raw message
        t_norm = re.sub(r'\bu\b', 'you', t)
        t_norm = re.sub(r'\bur\b', 'your', t_norm)

        # 1. SELF QUERY (Questions about FRIDAY's identity or capabilities)
        self_query_patterns = [
            r'^(?:who\s+are\s+you|what\s+are\s+you|what\s+is\s+your\s+name|what\s+can\s+you\s+do)[\.\!\?]?$',
            r'\b(?:tell\s+me\s+about\s+you|tell\s+me\s+about\s+u)\b',
            r'^(?:about\s+you|about\s+u|who\s+is\s+friday|who\s+is\s+jarvis)[\.\!\?]?$',
            r'\b(?:explain\s+what\s+you\s+can\s+do|your\s+capabilities|how\s+do\s+you\s+work)\b',
        ]
        for p in self_query_patterns:
            if re.search(p, t_norm):
                return {
                    "intent": Intent.SELF_QUERY,
                    "confidence": 0.98,
                    "entities": {"phrase": raw}
                }

        # 2. CREATIVE (Stories, Jokes, Poems)
        creative_patterns = [
            r'\b(?:tell\s+me\s+a\s+story|tell\s+a\s+story|write\s+a\s+story|create\s+a\s+story)\b',
            r'\b(?:tell\s+me\s+a\s+joke|make\s+me\s+laugh|say\s+something\s+funny)\b',
            r'\b(?:write\s+a\s+poem|compose\s+a\s+poem|write\s+a\s+song)\b',
        ]
        for p in creative_patterns:
            if re.search(p, t_norm):
                return {
                    "intent": Intent.CREATIVE,
                    "confidence": 0.95,
                    "entities": {"topic": raw}
                }

        # 3. GREETING & CONVERSATION
        greeting_patterns = [
            r'^(?:hello|hi|hey|greetings|howdy)(?:\s+(?:friday|jarvis))?[\.\!\?]?$',
            r'^(?:good\s+(?:morning|afternoon|evening|night|day))(?:\s+(?:friday|jarvis))?[\.\!\?]?$',
            r'^(?:how\s+are\s+you|how\s+was\s+your\s+day|how\s+are\s+things|how\'s\s+it\s+going)(?:\s+(?:friday|jarvis)|,\s*(?:friday|jarvis))?[\.\!\?]?$',
            r'^(?:can\s+you\s+talk|are\s+you\s+there|are\s+you\s+listening|you\s+there)(?:\s+(?:friday|jarvis))?[\.\!\?]?$',
            r'^(?:thank\s+you|thanks|thank\s+you\s+very\s+much|thanks\s+a\s+lot)(?:\s+(?:friday|jarvis))?[\.\!\?]?$',
        ]
        for p in greeting_patterns:
            if re.search(p, t_norm):
                return {
                    "intent": Intent.CONVERSATION,
                    "confidence": 0.98,
                    "entities": {"phrase": raw}
                }

        # 4. CALCULATOR & ARITHMETIC (e.g. 1/0, 25*4, 15% of 800, 27 squared, etc.)
        calc_patterns = [
            r'^(?:calculate|compute|solve|evaluate)\s+(.+)$',
            r'(\d+(?:\.\d+)?)\s*(?:multiplied\s+by|times|\*|x)\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:divided\s+by|\/|over)\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:%|percent)\s*of\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:squared|cubed)',
            r'add\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)',
            r'subtract\s+(\d+(?:\.\d+)?)\s+from\s+(\d+(?:\.\d+)?)',
            r'square\s+root\s+(?:of\s+)?(\d+(?:\.\d+)?)',
            r'^\s*([0-9\+\-\*\/\^\(\)\.\s]+)\s*$',
        ]
        is_followup_math = False
        if context and context.get("last_calc_result") is not None:
            has_two_operands = bool(re.search(r'\badd\s+\d+\s+and\s+\d+\b|\bsubtract\s+\d+\s+from\s+\d+\b', t_norm))
            if not has_two_operands:
                if re.search(r'\b(?:now|then|next)?\s*(?:divide|multiply|add|subtract|times|plus|minus)\s+(?:it\s+)?(?:by\s+)?(\d+(?:\.\d+)?)', t_norm) and ("it" in t_norm or "now" in t_norm or "then" in t_norm or t_norm.startswith(("+", "-", "*", "/"))):
                    is_followup_math = True

        if is_followup_math:
            return {
                "intent": Intent.CALCULATOR,
                "confidence": 0.95,
                "entities": {"expression": raw, "is_followup": True}
            }

        starts_with_calc = re.search(r'^(?:calculate|compute)\b', t_norm)
        if starts_with_calc or any(re.search(p, t_norm) for p in calc_patterns[1:]):
            if re.search(r'\d', t_norm) or "/" in t_norm or "*" in t_norm or "+" in t_norm or "-" in t_norm:
                return {
                    "intent": Intent.CALCULATOR,
                    "confidence": 0.95,
                    "entities": {"expression": raw}
                }

        m_what_math = re.search(r'^what\s+is\s+([0-9\s\+\-\*\/\^\(\)\.x]+)\??$', t_norm)
        if m_what_math and re.search(r'\d', m_what_math.group(1)):
            return {
                "intent": Intent.CALCULATOR,
                "confidence": 0.95,
                "entities": {"expression": m_what_math.group(1).strip()}
            }

        # 5. SCREENSHOT & VISION
        if re.search(r'\b(take\s+a?\s*screenshot|capture\s+(?:the\s+)?screen|grab\s+(?:the\s+)?screen|screenshot)\b', t_norm):
            return {
                "intent": Intent.SCREENSHOT,
                "confidence": 0.96,
                "entities": {}
            }
        if ("screenshot" in t_norm or "screen" in t_norm) and any(w in t_norm for w in ["what", "look", "analyze", "explain", "see", "wrong"]):
            return {
                "intent": Intent.SCREENSHOT,
                "confidence": 0.95,
                "entities": {"question": raw}
            }

        # 6. SYSTEM INFO
        system_patterns = [
            r'\b(?:cpu|ram|memory|battery|disk|hardware|system\s+usage|system\s+status|pc\s+status)\b',
            r'\b(?:check\s+(?:my\s+)?system|show\s+cpu|cpu\s+usage|check\s+system)\b',
        ]
        if any(re.search(p, t_norm) for p in system_patterns) and not re.search(r'\b(?:language|coffee|remember|forget)\b', t_norm):
            return {
                "intent": Intent.SYSTEM,
                "confidence": 0.95,
                "entities": {}
            }

        # 7. MEMORY (SAVE / RECALL / FORGET)
        if re.search(r'\b(forget|delete\s+memory|erase\s+memory)\b', t_norm):
            clean = re.sub(r'^(?:(?:friday|jarvis),?\s*)?(?:please\s+)?(?:forget\s+(?:that\s+)?(?:my\s+)?|delete\s+memory\s+|erase\s+memory\s+)', '', raw, flags=re.IGNORECASE).strip()
            clean = clean.replace("my", "").strip()
            if " is " in clean.lower():
                clean = clean.split(" is ")[0].strip()
            return {
                "intent": Intent.MEMORY,
                "confidence": 0.94,
                "entities": {"sub_action": "forget", "query": clean}
            }

        if re.search(r'\bremember\b', t_norm) and not re.search(r'\b(?:what|do you|did you)\b', t_norm):
            clean = raw
            for prefix in ["friday,", "friday", "jarvis,", "jarvis", "please", "can you", "remember that", "remember my", "remember:"]:
                if clean.lower().startswith(prefix):
                    clean = clean[len(prefix):].strip()
            return {
                "intent": Intent.MEMORY,
                "confidence": 0.94,
                "entities": {"sub_action": "save", "text": clean}
            }

        if re.search(r'\bwhat\s+is\s+my\b|\bwhat\s+do\s+you\s+remember\b|\bwhat\s+do\s+i\b|\brecall\s+my\b', t_norm):
            return {
                "intent": Intent.MEMORY,
                "confidence": 0.94,
                "entities": {"sub_action": "recall", "query": raw}
            }

        # 8. BROWSER & APPLICATION / COMPUTER CONTROL
        open_app_match = re.search(r'\b(?:open|launch|start|run|close|exit|terminate|kill|stop)\s+(?:application\s+|app\s+)?([a-zA-Z0-9\s\.\-_]+)', t_norm)
        if open_app_match:
            action_verb = open_app_match.group(0).split()[0].lower()
            target = open_app_match.group(1).strip().rstrip(".")
            if any(f in target for f in ["download", "desktop", "document", "folder", "directory"]):
                return {
                    "intent": Intent.COMPUTER_CONTROL,
                    "confidence": 0.95,
                    "entities": {"action": "open_folder", "target": target}
                }
            if target in ["browser", "chrome", "google chrome", "firefox", "edge"]:
                return {
                    "intent": Intent.BROWSER,
                    "confidence": 0.95,
                    "entities": {"action": "open_browser", "target": target}
                }
            if target and target not in ["a", "an", "the", "that", "this", "it"]:
                return {
                    "intent": Intent.COMPUTER_CONTROL,
                    "confidence": 0.93,
                    "entities": {"action": "close_app" if action_verb in ["close", "exit", "terminate", "kill", "stop"] else "open_app", "app_name": target}
                }

        # Folders directly
        if re.search(r'\b(?:downloads?|desktop|documents?)\b', t_norm) and re.search(r'\b(?:folder|directory|open|show)\b', t_norm):
            folder = "downloads" if "download" in t_norm else ("desktop" if "desktop" in t_norm else "documents")
            return {
                "intent": Intent.COMPUTER_CONTROL,
                "confidence": 0.95,
                "entities": {"action": "open_folder", "target": folder}
            }

        # File search & counting
        if re.search(r'\b(?:find|search|count|list)\b', t_norm) and re.search(r'\b(?:files?|pdfs?|python\s+files?|documents?)\b', t_norm):
            return {
                "intent": Intent.COMPUTER_CONTROL,
                "confidence": 0.93,
                "entities": {"action": "search_files", "query": raw}
            }

        # Largest files
        if re.search(r'\b(?:largest|biggest)\s+files?\b', t_norm):
            return {
                "intent": Intent.COMPUTER_CONTROL,
                "confidence": 0.93,
                "entities": {"action": "find_largest_files", "query": raw}
            }

        # 9. MULTI STEP TASK (Coding, Planning)
        coding_planning_patterns = [
            r'\b(?:write\s+a?\s*function|write\s+code|implement|generate\s+code|python\s+script|code\s+snippet|debug\s+code)\b',
            r'\b(?:how\s+to\s+code|write\s+a\s+program)\b',
            r'\b(?:create\s+a\s+plan|plan\s+for|break\s+down\s+task|step\s+by\s+step\s+plan)\b',
        ]
        if any(re.search(p, t_norm) for p in coding_planning_patterns):
            return {
                "intent": Intent.MULTI_STEP_TASK,
                "confidence": 0.90,
                "entities": {"task": raw}
            }

        # 10. TIMELESS KNOWLEDGE / GENERAL TOPICS
        timeless_topics = [
            r'\bwhy\s+is\s+the\s+sky\s+blue\b',
            r'\bexplain\s+quantum\s+computing\b|\bquantum\s+computing\b',
            r'\bcompare\s+python\s+(?:and|with)\s+java\b|\bpython\s+vs\s+java\b',
            r'\bwhich\s+is\s+your\s+favorite\s+(?:programming\s+)?language\b|\byour\s+favorite\s+language\b',
            r'\bwhat\s+is\s+python\b',
            r'\bwhat\s+is\s+ai\b',
        ]
        if any(re.search(p, t_norm) for p in timeless_topics):
            return {
                "intent": Intent.CONVERSATION,
                "confidence": 0.95,
                "entities": {"topic": raw}
            }

        # 11. CLARIFICATION (Vague, underspecified instructions)
        ambiguous_patterns = [
            r'^(?:do\s+that(?:\s+thing)?|handle\s+it|fix\s+this|take\s+care\s+of\s+it|just\s+do\s+it|do\s+it)[\.\!\?]?$',
            r'^(?:something|whatever|stuff)[\.\!\?]?$',
        ]
        if any(re.search(p, t_norm) for p in ambiguous_patterns):
            return {
                "intent": Intent.CLARIFICATION,
                "confidence": 0.90,
                "entities": {"ambiguous": True, "raw": raw}
            }

        # 12. RESEARCH (Explicit search/topic queries & Short noun phrases like "Naruto", "Free Fire", "Tesla", "tell me about lion")
        # Treat any non-clarification topic query as Intent.RESEARCH
        web_research_triggers = [
            r'^(?:search\s+for|search\s+web\s+for|google|look\s+up)\s+(.+)$',
            r'^(?:find\s+the\s+latest|latest\s+news|find\s+news)\s+(.+)$',
            r'\b(?:tell\s+me\s+about|research|find\s+out\s+about)\s+(.+)',
            r'\b(?:latest\s+ai\s+news|latest\s+nvidia\s+gpu|latest\s+tech\s+news|ai\s+news)\b',
            r'\bwhat\s+happened\s+(?:to|in|with)\s+(.+)',
            r'\bwho\s+is\s+(?:the\s+)?(?:current\s+)?([a-zA-Z\s]+)\??$',
            r'\bwhat\s+is\s+the\s+weather\b',
        ]
        for p in web_research_triggers:
            m = re.search(p, t_norm)
            if m:
                topic = m.group(1).strip() if m.groups() and m.group(1) else raw
                return {
                    "intent": Intent.RESEARCH,
                    "confidence": 0.92,
                    "entities": {"topic": topic, "query": topic}
                }

        # Any short phrase (1-4 words) or general topic request is treated as RESEARCH rather than CLARIFICATION
        return {
            "intent": Intent.RESEARCH,
            "confidence": 0.85,
            "entities": {"topic": raw, "query": raw}
        }

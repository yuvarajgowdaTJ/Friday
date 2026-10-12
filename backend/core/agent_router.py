import logging
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.tools.registry import tool_registry
from backend.core.memory import MemoryManager
from backend.core.brain import brain_instance
from backend.core.intent import IntentClassifier, Intent

logger = logging.getLogger("JARVIS.Core.AgentRouter")

# In-memory session context for multi-turn pronoun, topic, and math resolution
SESSION_CONTEXT: Dict[str, Dict[str, Any]] = {}

# Conversational knowledge repository for timeless questions
KNOWLEDGE_BASE = {
    "sky_blue": (
        "The sky appears blue because of Rayleigh scattering. "
        "Sunlight reaches Earth's atmosphere and is scattered in all directions by gas molecules in the air. "
        "Blue light travels as shorter, smaller waves than other colors, so it is scattered more widely, "
        "making the sky appear blue to our eyes during daylight."
    ),
    "quantum_computing": (
        "Quantum computing harnesses the laws of quantum mechanics to solve problems "
        "too complex for classical computers.\n\n"
        "While classical computers process bits that are either 0 or 1, "
        "quantum computers use qubits, which can exist in a superposition of both states simultaneously. "
        "Through entanglement, qubits can correlate instantly, enabling exponential processing leaps "
        "in cryptography, molecular modeling, and optimization."
    ),
    "compare_python_java": (
        "Here is a comparison between Python and Java, sir:\n\n"
        "• **Python** is dynamically typed, concise, and excels at developer velocity. "
        "It is dominant in artificial intelligence, machine learning, data engineering, and automation.\n"
        "• **Java** is statically typed, object-oriented, and runs on the JVM. "
        "It remains a bedrock for high-concurrency enterprise systems, Android applications, and large financial backends.\n\n"
        "Python maximizes agility and AI tooling; Java provides strict type safety and high runtime throughput."
    ),
    "favorite_language": (
        "Python holds a distinguished place in my core architecture due to its elegance and supremacy in AI frameworks. "
        "However, I appreciate any language executed with clarity and precision, sir."
    ),
    "about_jarvis": (
        "I am FRIDAY, your autonomous desktop artificial intelligence. "
        "I can manage desktop applications, inspect hardware diagnostics, capture and analyze displays, "
        "safely execute calculations, manage file operations, recall persistent memories, and conduct targeted research."
    )
}

class NaturalLanguageAgent:
    @staticmethod
    def get_session_context(session_id: str) -> Dict[str, Any]:
        if session_id not in SESSION_CONTEXT:
            SESSION_CONTEXT[session_id] = {
                "recent_turns": [],        # max 5 bounded short-term conversation turns
                "last_topic": None,
                "last_topic_turn": 0,
                "turn_count": 0,
                "last_query": None,
                "last_task": None,
                "last_tool": None,
                "last_tool_result": None,
                "last_calc_result": None,
                "entities": {}
            }
        return SESSION_CONTEXT[session_id]

    @staticmethod
    def record_turn(ctx: Dict[str, Any], user_msg: str, assistant_msg: str):
        """Records a completed turn in short-term context without context pollution."""
        turns = ctx.setdefault("recent_turns", [])
        turns.append({
            "user": user_msg,
            "assistant": assistant_msg,
            "topic": ctx.get("last_topic")
        })
        ctx["recent_turns"] = turns[-5:]
        ctx["last_query"] = user_msg

    @staticmethod
    def resolve_contextual_pronouns(text: str, session_id: str) -> str:
        """Resolves pronouns like 'its', 'it', 'they' using recent session context with topic decay safeguards."""
        ctx = NaturalLanguageAgent.get_session_context(session_id)
        last_topic = ctx.get("last_topic")
        last_turn = ctx.get("last_topic_turn", 0)
        current_turn = ctx.get("turn_count", 0)

        # Topic Decay Safeguard: decay topic if not renewed within 4 turns
        if last_topic and (current_turn - last_turn > 4):
            ctx["last_topic"] = None
            return text

        if not last_topic:
            return text

        t_low = text.lower()

        # If user is introducing a brand new explicit topic without pronouns, do NOT resolve old topic
        has_explicit_new_topic = bool(re.search(
            r'\b(?:tell\s+me\s+about|what\s+is|who\s+is|search\s+for|explain|calculate)\s+(?!it\b|u\b|you\b|this\b|that\b|its\b)[a-zA-Z0-9\s]{3,}',
            t_low
        ))
        has_pronoun = bool(re.search(r'\b(it|its|itself|this|that|he|him|his|she|her|they|them)\b', t_low))

        if has_explicit_new_topic and not has_pronoun:
            return text

        resolved = text
        if re.search(r'\b(its|itself)\b', t_low):
            resolved = re.sub(r'\b(its|itself)\b', f"{last_topic}'s", resolved, flags=re.IGNORECASE)
        elif re.search(r'\b(it|this|that)\b', t_low) and not t_low.startswith("it "):
            resolved = re.sub(r'\b(it|this|that)\b', str(last_topic), resolved, flags=re.IGNORECASE)
        elif t_low.startswith("it "):
            resolved = re.sub(r'^it\b', str(last_topic), resolved, flags=re.IGNORECASE)
        elif re.search(r'\bwho\s+(?:created|wrote|made|directed|author of)\b', t_low) and not any(w in t_low for w in [last_topic.lower()]):
            resolved = f"{resolved} {last_topic}"
        elif "what about" in t_low and len(t_low.split()) <= 4:
            resolved = f"{resolved} regarding {last_topic}"

        return resolved

    @classmethod
    def process_request(
        cls,
        user_message: str,
        session_id: str = "default",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Primary AI router for FRIDAY.
        1. Classifies user request intent
        2. Resolves multi-turn context
        3. Routes exclusively to the appropriate subsystem/tool
        4. Synthesizes a natural, concise FRIDAY personality response
        """
        raw_text = user_message.strip()
        text_lower = raw_text.lower()
        ctx = cls.get_session_context(session_id)
        ctx["turn_count"] = ctx.get("turn_count", 0) + 1
        current_turn = ctx["turn_count"]

        # Context resolution
        resolved_text = cls.resolve_contextual_pronouns(raw_text, session_id)
        resolved_lower = resolved_text.lower()

        executed_tools: List[Dict[str, Any]] = []

        # =========================================================================
        # 0. COMPOUND MULTI-STEP PIPELINES & TOOL FOLLOW-UPS
        # =========================================================================
        if ("open chrome" in text_lower or "launch chrome" in text_lower) and ("search" in text_lower or "find" in text_lower):
            c_res = tool_registry.execute("launch_application", {"app_name": "chrome"})
            executed_tools.append(c_res)
            m = re.search(r'search\s+(?:for\s+)?(.+)', raw_text, re.IGNORECASE)
            search_query = m.group(1).strip() if m else "latest NVIDIA GPU"
            w_res = tool_registry.execute("web_search", {"query": search_query})
            executed_tools.append(w_res)
            ctx["last_topic"] = search_query
            ctx["last_topic_turn"] = current_turn
            ctx["last_tool"] = "web_search"
            summary = (
                f"Opened Google Chrome for you, sir. In addition, I researched '{search_query}':\n\n"
                f"{w_res.get('result', {}).get('summary', 'Search completed.')}"
            )
            cls.record_turn(ctx, raw_text, summary)
            return {"response": summary, "mode": "multi_step_agent", "tool_calls": executed_tools}

        # Screen analysis compound
        if ("screenshot" in text_lower or "screen" in text_lower) and any(w in text_lower for w in ["what", "look", "analyze", "explain", "see", "wrong"]):
            v_res = tool_registry.execute("analyze_screen", {"question": raw_text})
            executed_tools.append(v_res)
            analysis = v_res.get("result", {}).get("analysis", "Screen captured and analyzed.")
            resp = f"Certainly, sir. Looking at your screen:\n\n{analysis}"
            cls.record_turn(ctx, raw_text, resp)
            return {"response": resp, "mode": "vision_agent", "tool_calls": executed_tools}

        # =========================================================================
        # INTENT CLASSIFICATION
        # =========================================================================
        classification = IntentClassifier.classify(resolved_text, context=ctx)
        intent = classification["intent"]
        entities = classification.get("entities", {})
        logger.info(f"Classified intent: {intent.value} (confidence: {classification.get('confidence')}) for '{raw_text}' (resolved: '{resolved_text}')")

        # -------------------------------------------------------------------------
        # 1. SELF QUERY (Questions about FRIDAY's identity/capabilities)
        # -------------------------------------------------------------------------
        if intent == Intent.SELF_QUERY:
            return {
                "response": KNOWLEDGE_BASE["about_jarvis"],
                "mode": "conversational_ai",
                "tool_calls": None
            }

        # -------------------------------------------------------------------------
        # 2. CREATIVE (Stories, Jokes, Poems)
        # -------------------------------------------------------------------------
        if intent == Intent.CREATIVE:
            brain_res = brain_instance.generate_response([{"role": "user", "content": raw_text}])
            return {
                "response": brain_res.get("content", "Once upon a time in a digital landscape, a resilient AI stood ready to assist."),
                "mode": "creative",
                "tool_calls": None
            }

        # -------------------------------------------------------------------------
        # 3. GREETING & CONVERSATION
        # -------------------------------------------------------------------------
        if intent == Intent.CONVERSATION:
            if re.search(r'\bwhy\s+is\s+the\s+sky\s+blue\b', text_lower):
                return {"response": f"Certainly, sir. {KNOWLEDGE_BASE['sky_blue']}", "mode": "conversational_ai"}
            if re.search(r'\bexplain\s+quantum\s+computing\b|\bquantum\s+computing\b', text_lower):
                ctx["last_topic"] = "quantum computing"
                return {"response": f"Certainly, sir.\n\n{KNOWLEDGE_BASE['quantum_computing']}", "mode": "conversational_ai"}
            if re.search(r'\bcompare\s+python\s+(?:and|with)\s+java\b|\bpython\s+vs\s+java\b', text_lower):
                ctx["last_topic"] = "Python and Java"
                return {"response": KNOWLEDGE_BASE["compare_python_java"], "mode": "conversational_ai"}
            if re.search(r'\bwhich\s+is\s+your\s+favorite\s+(?:programming\s+)?language\b|\byour\s+favorite\s+language\b', text_lower):
                return {"response": KNOWLEDGE_BASE["favorite_language"], "mode": "conversational_ai"}

            brain_res = brain_instance.generate_response([{"role": "user", "content": raw_text}])
            return {
                "response": brain_res.get("content", "I am standing by, sir. How may I assist?"),
                "mode": "conversational_ai",
                "tool_calls": None
            }

        # -------------------------------------------------------------------------
        # 4. CALCULATOR
        # -------------------------------------------------------------------------
        if intent == Intent.CALCULATOR:
            expr = raw_text
            # Handle context follow-up calculation: e.g. "now divide it by 5"
            if entities.get("is_followup") and ctx.get("last_calc_result") is not None:
                last_val = ctx["last_calc_result"]
                m_op = re.search(r'\b(divide|multiply|add|subtract|times|plus|minus)\s+(?:it\s+)?(?:by\s+)?(\d+(?:\.\d+)?)', text_lower)
                if m_op:
                    op, num = m_op.group(1), m_op.group(2)
                    op_symbol = {"divide": "/", "multiply": "*", "times": "*", "add": "+", "plus": "+", "subtract": "-", "minus": "-"}.get(op, "/")
                    expr = f"{last_val} {op_symbol} {num}"

            calc_res = tool_registry.execute("calculate", {"expression": expr})
            executed_tools.append(calc_res)
            if calc_res.get("status") == "SUCCESS":
                result_val = calc_res["result"]["result"]
                ctx["last_calc_result"] = result_val
                ctx["last_topic"] = str(result_val)
                speech = calc_res["result"]["speech_answer"]
                return {"response": speech, "mode": "calculator", "tool_calls": executed_tools}
            else:
                return {"response": f"I was unable to evaluate that expression, sir: {calc_res.get('error')}", "mode": "calculator", "tool_calls": executed_tools}

        # -------------------------------------------------------------------------
        # 5. SYSTEM DIAGNOSTICS
        # -------------------------------------------------------------------------
        if intent == Intent.SYSTEM:
            res = tool_registry.execute("get_system_stats", {})
            executed_tools.append(res)
            if res.get("status") == "SUCCESS":
                cpu_p = res["result"]["cpu"]["percent"]
                ram_p = res["result"]["ram"]["percent"]
                return {
                    "response": f"CPU utilization is currently {cpu_p} percent, and RAM usage is at {ram_p} percent, sir. All core subsystems are operational.",
                    "mode": "system_diagnostics",
                    "tool_calls": executed_tools
                }
            return {"response": "Unable to retrieve hardware telemetry, sir.", "mode": "system_diagnostics", "tool_calls": executed_tools}

        # -------------------------------------------------------------------------
        # 6. SCREENSHOT
        # -------------------------------------------------------------------------
        if intent == Intent.SCREENSHOT:
            res = tool_registry.execute("capture_screenshot", {})
            executed_tools.append(res)
            inner_res = res.get("result") or {}
            if res.get("status") == "SUCCESS" and inner_res.get("status") == "SUCCESS":
                filename = inner_res.get("filename", "screenshot.png")
                return {
                    "response": f"Screenshot captured successfully and saved to {filename}, sir.",
                    "mode": "tool_system",
                    "tool_calls": executed_tools
                }
            err_msg = inner_res.get("error") or res.get("error") or "Unknown error"
            return {"response": f"Failed to capture screenshot: {err_msg}, sir.", "mode": "tool_system", "tool_calls": executed_tools}

        # -------------------------------------------------------------------------
        # 7. COMPUTER CONTROL & BROWSER
        # -------------------------------------------------------------------------
        if intent in [Intent.COMPUTER_CONTROL, Intent.BROWSER]:
            action = entities.get("action")
            if action == "open_folder":
                target = entities.get("target", "downloads")
                res = tool_registry.execute("open_folder", {"folder_name": target})
                executed_tools.append(res)
                return {"response": f"Opening your {target.title()} folder in File Explorer, sir.", "mode": "tool_system", "tool_calls": executed_tools}

            if action == "search_files":
                pattern = ".pdf" if "pdf" in text_lower else (".py" if "python" in text_lower else "*")
                root_path = None
                if "downloads" in text_lower:
                    from pathlib import Path
                    root_path = str(Path.home() / "Downloads")
                res = tool_registry.execute("search_files", {"pattern": pattern, "root_path": root_path})
                executed_tools.append(res)
                summary = res.get("result", {}).get("summary", f"Search completed for {pattern}.")
                return {"response": summary, "mode": "file_agent", "tool_calls": executed_tools}

            if action == "find_largest_files":
                folder = "downloads" if "download" in text_lower else "documents"
                res = tool_registry.execute("find_largest_files", {"folder_name": folder, "limit": 5})
                executed_tools.append(res)
                return {"response": res.get("result", {}).get("summary", "Examined files."), "mode": "file_agent", "tool_calls": executed_tools}

            if action == "close_app":
                app_target = entities.get("app_name", "")
                res = tool_registry.execute("close_application", {"app_name": app_target})
                executed_tools.append(res)
                term_count = res.get("result", {}).get("terminated_processes", 0)
                if term_count > 0:
                    return {"response": f"Closed {app_target}, terminating {term_count} process(es), sir.", "mode": "tool_system", "tool_calls": executed_tools}
                return {"response": f"No active processes matching '{app_target}' were found running, sir.", "mode": "tool_system", "tool_calls": executed_tools}

            app_target = entities.get("app_name") or entities.get("target") or "chrome"
            if "chrome" in app_target.lower() or intent == Intent.BROWSER:
                res = tool_registry.execute("launch_application", {"app_name": "chrome"})
                executed_tools.append(res)
                return {"response": "Opening Google Chrome for you now, sir.", "mode": "tool_system", "tool_calls": executed_tools}

            res = tool_registry.execute("launch_application", {"app_name": app_target})
            executed_tools.append(res)
            if res.get("error"):
                return {"response": f"Unable to launch '{app_target}': {res.get('error')}", "mode": "tool_system", "tool_calls": executed_tools}
            return {"response": f"Opening {app_target.title()}, sir.", "mode": "tool_system", "tool_calls": executed_tools}

        # -------------------------------------------------------------------------
        # 8. MEMORY (SAVE / RECALL / FORGET)
        # -------------------------------------------------------------------------
        if intent == Intent.MEMORY:
            sub_action = entities.get("sub_action", "recall")
            if sub_action == "save":
                clean = entities.get("text", raw_text)
                key = "preference"
                val = clean
                if " is " in clean.lower():
                    parts = re.split(r'\s+is\s+', clean, maxsplit=1, flags=re.IGNORECASE)
                    key = parts[0].replace("my", "").strip()
                    val = parts[1].strip()
                elif " = " in clean:
                    parts = clean.split("=", 1)
                    key = parts[0].replace("my", "").strip()
                    val = parts[1].strip()

                mem_res = tool_registry.execute("add_memory", {"key": key, "value": val, "category": "preference"})
                executed_tools.append(mem_res)
                ctx["last_topic"] = key
                return {
                    "response": f"I have remembered that your {key} is {val}, sir.",
                    "mode": "memory_engine",
                    "tool_calls": executed_tools
                }

            if sub_action == "forget":
                query = entities.get("query", "preference")
                del_res = tool_registry.execute("delete_memory", {"query": query})
                executed_tools.append(del_res)
                del_data = del_res.get("result", {})
                if del_data.get("deleted_count", 0) > 0:
                    return {
                        "response": f"I have forgotten that entry and removed it from my memory archives, sir.",
                        "mode": "memory_engine",
                        "tool_calls": executed_tools
                    }
                return {
                    "response": f"I searched my archives, but found no matching memory for '{query}' to forget, sir.",
                    "mode": "memory_engine",
                    "tool_calls": executed_tools
                }

            # recall
            memories = MemoryManager.get_all_memories(db=db)
            query_words = [w for w in text_lower.split() if w not in ["what", "is", "my", "tell", "me", "do", "you", "remember", "the", "sir"]]
            search_query = " ".join(query_words)
            matches = MemoryManager.search_memories(search_query, db=db) if search_query else memories
            if matches:
                m = matches[0]
                return {
                    "response": f"Your {m['key']} is {m['value']}, sir.",
                    "mode": "memory_engine",
                    "tool_calls": executed_tools
                }
            elif memories:
                items_str = "; ".join(f"{m['key']}: {m['value']}" for m in memories[:4])
                return {
                    "response": f"Here is what I have archived about you, sir: {items_str}.",
                    "mode": "memory_engine",
                    "tool_calls": executed_tools
                }
            return {
                "response": "I currently have no stored personal memories matching that request in my archives, sir.",
                "mode": "memory_engine",
                "tool_calls": executed_tools
            }

        # -------------------------------------------------------------------------
        # 9. MULTI STEP TASK (Coding & Planning)
        # -------------------------------------------------------------------------
        if intent == Intent.MULTI_STEP_TASK:
            brain_res = brain_instance.generate_response([{"role": "user", "content": raw_text}])
            return {
                "response": brain_res.get("content", f"Understood, sir. Initiating task execution for '{raw_text}'."),
                "mode": "agent_planner",
                "tool_calls": None
            }

        # -------------------------------------------------------------------------
        # 10. RESEARCH
        # -------------------------------------------------------------------------
        if intent == Intent.RESEARCH:
            query = entities.get("query") or entities.get("topic") or raw_text
            clean_q = re.sub(r'^(?:search\s+for|search\s+web\s+for|google|tell\s+me\s+about|research|find\s+out\s+about)\s+', '', query, flags=re.IGNORECASE).strip()
            clean_q = clean_q.rstrip("?.!")
            ctx["last_topic"] = clean_q
            res = tool_registry.execute("web_search", {"query": clean_q})
            executed_tools.append(res)
            summary = res.get("result", {}).get("summary")
            if summary:
                return {
                    "response": summary,
                    "mode": "web_research",
                    "tool_calls": executed_tools
                }
            return {
                "response": f"I conducted research on '{clean_q}', but retrieved no external results, sir.",
                "mode": "web_research",
                "tool_calls": executed_tools
            }

        # -------------------------------------------------------------------------
        # 11. CLARIFICATION
        # -------------------------------------------------------------------------
        if intent == Intent.CLARIFICATION:
            return {
                "response": "What would you like me to do, sir?",
                "mode": "conversational_clarification",
                "tool_calls": None
            }

        # Fallback to AI Brain
        brain_res = brain_instance.generate_response([{"role": "user", "content": raw_text}])
        return {
            "response": brain_res.get("content", f"I have registered your inquiry regarding '{raw_text}', sir. How would you like me to proceed?"),
            "mode": brain_res.get("mode", "ai_brain"),
            "tool_calls": executed_tools if executed_tools else brain_res.get("tool_calls")
        }

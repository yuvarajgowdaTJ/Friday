import logging
import random
from typing import List, Dict, Any, Optional
from openai import OpenAI
from backend.config import settings

logger = logging.getLogger("JARVIS.Brain")

SYSTEM_PROMPT = """You are FRIDAY, an advanced, highly intelligent personal AI assistant operating on a Windows system.

Personality traits:
- Intelligent, calm, concise, professional, slightly futuristic, naturally helpful.
- Address the user with natural respect ("sir" or by name if remembered), but do NOT put "sir" into every sentence.
- Answers concisely without unnecessary fluff. Efficient, precise, and proactive.
- Avoid repetitive canned responses like "Certainly, sir" or "Of course, sir".
"""

# Varied natural responses for conversational interactions
GREETING_RESPONSES = [
    "Good day, sir. FRIDAY is online. How may I assist you?",
    "Greetings, sir. FRIDAY subsystems are operational and ready.",
    "Good to hear from you, sir. FRIDAY is ready. How may I be of assistance?",
    "Online and listening, sir. FRIDAY at your service. What are we working on?",
    "FRIDAY is online and at your service, sir. How can I help today?"
]

STATUS_RESPONSES = [
    "Quite productive, sir. Systems are running smoothly and ready for your command.",
    "All diagnostics are green and operational, sir. Ready when you are.",
    "Operating at peak efficiency, sir. How are things with you?",
    "Everything is nominal, sir. What shall we tackle next?"
]

PRESENCE_RESPONSES = [
    "I am here, sir. Standing by.",
    "Always listening, sir. Ready when you are.",
    "Present and operational, sir. How can I assist?",
    "Right here, sir. How may I help?"
]

TALK_RESPONSES = [
    "Yes, I can communicate via voice and text, sir. What would you like to discuss?",
    "Indeed, sir. My conversational and voice processing systems are active.",
    "Fully capable of speech and interaction, sir. How can I help?"
]

THANKS_RESPONSES = [
    "You are very welcome, sir.",
    "Glad to be of service, sir.",
    "My pleasure, sir.",
    "Anytime, sir."
]

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs, sir.",
    "There are 10 types of people in the world: those who understand binary, and those who don't.",
    "Why did the neural network cross the road? To optimize the loss function on the other side, sir.",
    "An SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'"
]

CLARIFICATION_RESPONSES = [
    "What would you like me to do, sir?",
    "Could you specify what you would like me to handle, sir?",
    "Please clarify what action you would like me to perform, sir."
]

class JarvisBrain:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.client = None

        if self.api_key and self.api_key.startswith("sk-"):
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized with model {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.info("No valid OpenAI API key provided. Operating in Offline/Fallback Mode.")

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generates a response from OpenAI or fallback engine.
        Returns dict with keys: 'content', 'tool_calls', 'mode' ('online' | 'offline').
        """
        if self.client:
            try:
                formatted_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
                kwargs = {
                    "model": self.model,
                    "messages": formatted_messages,
                    "temperature": temperature,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = self.client.chat.completions.create(**kwargs)
                choice = response.choices[0].message
                
                tool_calls_data = None
                if choice.tool_calls:
                    tool_calls_data = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in choice.tool_calls
                    ]

                return {
                    "content": choice.content or "",
                    "tool_calls": tool_calls_data,
                    "mode": "online"
                }
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}. Falling back to offline brain.")

        # Offline / Fallback Intelligent Response Logic
        return self._offline_response(messages)

    def _offline_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Natural, varied conversational responses for offline development & testing."""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").strip()
                break

        msg_low = last_user_msg.lower()

        # Jokes
        if any(w in msg_low for w in ["joke", "laugh", "funny"]):
            reply = random.choice(JOKES)
        # Ambiguous / clarification requests
        elif any(msg_low == p for p in ["do that", "handle it", "fix this", "do that thing", "take care of it", "just do it"]):
            reply = random.choice(CLARIFICATION_RESPONSES)
        # How was your day / how are you
        elif "how was your day" in msg_low:
            reply = "Quite productive, sir. I'm ready for whatever you'd like to work on."
        elif "how are you" in msg_low or "how's it going" in msg_low:
            reply = random.choice(STATUS_RESPONSES)
        # Are you there / can you talk
        elif "can you talk" in msg_low:
            reply = random.choice(TALK_RESPONSES)
        elif any(w in msg_low for w in ["are you there", "you there", "listening"]):
            reply = random.choice(PRESENCE_RESPONSES)
        # Thanks
        elif any(w in msg_low for w in ["thank you", "thanks"]):
            reply = random.choice(THANKS_RESPONSES)
        # Greetings
        elif any(w in msg_low for w in ["hello", "hi", "hey", "good morning", "good evening", "good day", "good night"]):
            reply = random.choice(GREETING_RESPONSES)
        elif "who are you" in msg_low or "what are you" in msg_low:
            reply = "I am FRIDAY, your autonomous personal AI assistant. All subsystems are operational."
        elif "what is python" in msg_low or msg_low == "python":
            reply = "Python is a high-level, versatile programming language renowned for its readability, expressive syntax, and rich ecosystem across artificial intelligence, automation, and backend engineering."
        elif "cpu" in msg_low or "ram" in msg_low or "hardware" in msg_low:
            reply = "All hardware monitoring telemetry is active and nominal, sir."
        elif "remember" in msg_low:
            reply = "I have updated my memory archives with that information, sir."
        else:
            reply = f"I have noted your request regarding '{last_user_msg}', sir. How would you like me to proceed?"

        return {
            "content": reply,
            "tool_calls": None,
            "mode": "offline"
        }

brain_instance = JarvisBrain()

import json
import sys
import os
import logging
from typing import Dict, Any, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger import get_logger

logger = get_logger("Planner")

try:
    from llm.groq_client import llm_client
except ImportError:
    llm_client = None

# ... (Keep your existing TOOLS and helper functions: extract_json, validate_plan, build_tools_description) ...
# COPY PASTE YOUR EXISTING TOOLS DICTIONARY AND HELPER FUNCTIONS HERE
TOOLS = {
    "get_movie_title_from_search": "Use this if the user describes a movie but doesn't give the exact name.",
    "search_movie_details": "Use this ONLY when you have a specific movie title.",
    "get_youtube_trailer": "Fetch the YouTube trailer URL for a movie",
    "get_streaming_info": "Find where the movie is available for streaming"
}
VALID_TOOLS = set(TOOLS.keys())

def extract_json(text: str) -> Optional[str]:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == -1: return None
    return text[start:end]

def validate_plan(plan: Dict[str, Any]) -> bool:
    if "steps" not in plan or not isinstance(plan["steps"], list): return False
    for step in plan["steps"]:
        if not isinstance(step, dict): return False
        if step["tool"] not in VALID_TOOLS: return False
    return True

def build_tools_description() -> str:
    return "\n".join(f"{i+1}. {name}(query): {desc}" for i, (name, desc) in enumerate(TOOLS.items()))

class PlannerAgent:
    def __init__(self):
        if llm_client is None: raise RuntimeError("LLM Client is not initialized.")
        self.llm = llm_client

    # 1. UPDATED SIGNATURE: Accept chat_history
    def create_plan(self, user_request: str, chat_history: str = "", retries: int = 2):
        logger.info(f"Received request: '{user_request}'")
        
        # 2. UPDATED PROMPT: Include History
        prompt = f"""
You are an AI Planner Agent.

Your task is to break down a user's request into a sequence of steps.

AVAILABLE TOOLS:
{build_tools_description()}

CONTEXT (PREVIOUS CONVERSATION):
{chat_history}

RULES:
1. Return ONLY a valid JSON object.
2. The JSON MUST follow this schema:
   {{
       "steps": [
           {{ "step_id": 1, "tool": "tool_name", "args": "argument", "description": "Short explanation" }}
       ]
   }}
3. **CRITICAL ARGUMENT RULES**:
   - IF the user refers to a previous movie (e.g., "Who directed it?", "Show me the trailer"), look at the CONTEXT to find the movie title. Use that title.
   - IF the user gives a new specific title, use that.
   - IF the user asks a vague question, start with 'get_movie_title_from_search'.
   - **FOR SUBSEQUENT STEPS**: Use "THE_MOVIE" as the placeholder argument.

USER REQUEST:
<<< {user_request} >>>

PLAN (JSON ONLY):
"""
        for attempt in range(retries + 1):
            try:
                response_text = self.llm.generate_text(prompt)
                clean_json = extract_json(response_text)
                if not clean_json: raise ValueError("No JSON found")
                
                plan = json.loads(clean_json)
                if not validate_plan(plan): raise ValueError("Invalid plan")
                
                for index, step in enumerate(plan["steps"], start=1):
                    step["step_id"] = index
                    
                return plan
            except Exception as e:
                logger.error(f"Planning failed attempt {attempt}: {e}")
                if attempt == retries: return None
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger import get_logger
from tools.movie_tools import search_movie_details, get_youtube_trailer, get_streaming_info, get_movie_title_from_search

logger = get_logger("Executor")

class ExecutorAgent:
    def __init__(self):
        self.tool_map = {
            "search_movie_details": search_movie_details,
            "get_youtube_trailer": get_youtube_trailer,
            "get_streaming_info": get_streaming_info,
            "get_movie_title_from_search": get_movie_title_from_search
        }

    def execute_plan(self, plan):
        results = {}
        context_movie_title = None 
        
        logger.info("Starting execution phase...")

        for step in plan.get("steps", []):
            tool_name = step.get("tool")
            arg = str(step.get("args")) # Force string conversion
            step_id = step.get("step_id")
            
            # --- 1. DETECT PLACEHOLDERS (Aggressive Regex) ---
            # Catches: [OUTPUT], {step_1}, THE_MOVIE, previous_result, etc.
            is_placeholder = bool(re.search(r'(\[.*?\]|\{.*?\}|OUTPUT|STEP|THE_MOVIE|placeholder|output of step \d+)', arg, re.IGNORECASE))

            # --- 2. CONTEXT REPLACEMENT ---
            if context_movie_title:
                # If we know the movie, ALWAYS replace the argument if it looks generic or is a placeholder
                if is_placeholder or tool_name != "get_movie_title_from_search":
                    logger.info(f"🔄 Replacing '{arg}' with discovered title '{context_movie_title}'")
                    arg = context_movie_title
            
            elif is_placeholder:
                # CRITICAL: If we have a placeholder but NO title, the previous step failed.
                # STOP. Do not call OMDb with "[OUTPUT FROM STEP 1]".
                error_msg = f"Error: Previous step failed to find a movie title. Cannot execute {tool_name}."
                logger.error(error_msg)
                results[tool_name] = error_msg
                continue 

            # --- 3. EXECUTION ---
            try:
                logger.info(f"Executing Step {step_id}: {tool_name}('{arg}')")
                
                output = self.tool_map[tool_name](arg)
                results[tool_name] = output
                
                # --- 4. CAPTURE TITLE ---
                if tool_name == "get_movie_title_from_search":
                    # Check if the tool actually found something
                    if isinstance(output, str) and "Found via search:" in output:
                        context_movie_title = output.replace("Found via search:", "").strip()
                        logger.info(f"🎯 Discovered Target Movie: {context_movie_title}")
                    else:
                        logger.warning(f"⚠️ Search step finished but didn't return a clear title. Output: {output[:50]}...")

                # Also capture from OMDb if that was the first step
                elif tool_name == "search_movie_details" and isinstance(output, dict) and "title" in output:
                    context_movie_title = output['title']

            except Exception as e:
                logger.error(f"Step {step_id} Failed: {e}")
                results[tool_name] = f"Error: {str(e)}"

        return results
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logger import get_logger

logger = get_logger("Verifier")

try:
    from llm.groq_client import llm_client
except ImportError:
    llm_client = None

class VerifierAgent:
    def __init__(self):
        self.llm = llm_client
        if self.llm is None:
            logger.critical("LLM Client is not initialized! Verifier cannot generate text.")

    def verify_and_respond(self, user_query, execution_results):
        logger.info("Verifying results and generating response...")

        if self.llm is None:
            return "I apologize, but my language engine is currently offline."

        # --- SMART VALIDATION ---
        
        # 1. Did OMDb work?
        omdb_result = execution_results.get("search_movie_details")
        omdb_success = False
        if omdb_result and isinstance(omdb_result, dict) and "Error" not in omdb_result:
            omdb_success = True

        # 2. Did Search work? (Crucial for Alita & Mission Impossible)
        search_result = execution_results.get("get_movie_title_from_search")
        search_success = False
        if search_result and isinstance(search_result, str) and "Found via search:" in search_result:
            search_success = True

        # DECISION: It counts as found if EITHER works
        movie_found = omdb_success or search_success

        if not movie_found:
            # THIS IS THE NEW MESSAGE. If you don't see this in logs, the file didn't save.
            logger.warning("Validation: No valid movie title or details found.") 
        
        # --- PREPARE CONTEXT ---
        movie_name_display = "Unknown"
        if omdb_success:
            movie_name_display = omdb_result.get('title', 'Unknown')
        elif search_success:
            movie_name_display = search_result.replace("Found via search:", "").strip()

        context = f"""
        User Query: "{user_query}"
        STATUS: {"Movie Found" if movie_found else "Movie Not Found"}
        Movie Name Identified: {movie_name_display}
        
        Tool Outputs:
        1. OMDb Details: {omdb_result if omdb_result else "Not executed/Not found"}
        2. Trailer Link: {execution_results.get('get_youtube_trailer', 'Not found')}
        """

        prompt = f"""
        You are the Verifier Agent.
        CONTEXT:
        {context}

        INSTRUCTIONS:
        - IF STATUS is "Movie Not Found": Apologize and ask for clarification.
        - IF STATUS is "Movie Found":
          - State the movie name clearly: "{movie_name_display}".
          - Provide the trailer link if available.
          - Do NOT say "I couldn't find details" if you have the name and trailer. Be helpful.

        FINAL RESPONSE:
        """

        try:
            return self.llm.generate_text(prompt)
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return "I found the movie, but I'm having trouble summarizing it right now."
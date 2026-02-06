import os
import logging
from dotenv import load_dotenv

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


def init_agents():
    """
    Initialize and return all agents.
    """
    planner = PlannerAgent()
    executor = ExecutorAgent()
    verifier = VerifierAgent()
    return planner, executor, verifier


def main():
    planner, executor, verifier = init_agents()

    logging.info("🍿 AI Movie Night Planner Initialized! (Type 'exit' to quit)")
    logging.info("----------------------------------------------------------")

    while True:
        try:
            # 1. Get user input
            user_query = input("\n👤 You: ").strip()

            if user_query.lower() in {"exit", "quit"}:
                logging.info("👋 Goodbye! Session ended.")
                break

            if not user_query:
                continue

            # --- Phase 1: Planning ---
            logging.info("🧠 Planning...")
            plan = planner.create_plan(user_query)

            if not plan or "steps" not in plan:
                logging.error("❌ Failed to generate a valid plan. Please try again.")
                continue

            # --- Phase 2: Execution ---
            logging.info("⚙️ Executing...")
            execution_results = executor.execute_plan(plan)

            if not execution_results:
                logging.error("❌ Execution failed or returned no results.")
                continue

            # --- Phase 3: Verification & Response ---
            logging.info("📝 Verifying...")
            final_response = verifier.verify_and_respond(
                user_query,
                execution_results
            )

            print(f"\nAssistant:\n{final_response}")

        except Exception:
            logging.exception("Unexpected error occurred in main loop")


if __name__ == "__main__":
    main()

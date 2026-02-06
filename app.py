import streamlit as st
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from logger import get_logger
import os

# Page Config
st.set_page_config(page_title="AI Movie Assistant", page_icon="🎬", layout="wide")

# Custom CSS for chat bubbles
st.markdown("""
<style>
    .user-msg { text-align: right; background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 5px 0; color: black; }
    .bot-msg { text-align: left; background-color: #e8f0fe; padding: 10px; border-radius: 10px; margin: 5px 0; color: black; }
</style>
""", unsafe_allow_html=True)

logger = get_logger("StreamlitApp")

def main():
    st.title("🎬 AI Movie Agent")
    st.write("Ask me about movies, trailers, ratings, or plot summaries!")

    # --- 1. INITIALIZE MEMORY ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Controls")
        if st.button("🧹 Clear Conversation"):
            st.session_state.messages = []
            if os.path.exists("search_cache.json"):
                os.remove("search_cache.json")
            st.rerun()

    # --- 2. DISPLAY HISTORY ---
    # We display previous messages so the user sees the conversation flow
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- 3. HANDLE NEW INPUT ---
    if prompt := st.chat_input("How can I help you today?"):
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # --- PREPARE CONTEXT STRING ---
        # Convert the last 3 turns into a string for the Planner
        # Format: "User: ... \n Agent: ..."
        history_text = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[-4:]]
        )

        # Run Agents
        with st.spinner("Thinking..."):
            try:
                # Initialize Agents
                planner = PlannerAgent()
                executor = ExecutorAgent()
                verifier = VerifierAgent()

                # Plan (With History!)
                plan = planner.create_plan(prompt, chat_history=history_text)
                
                if plan:
                    with st.status("⚙️ Executing Logic...", expanded=False) as status:
                        st.json(plan)
                        
                        # Execute
                        results = executor.execute_plan(plan)
                        st.write("✅ Tools Executed")
                        st.json(results)
                        status.update(label="Process Complete", state="complete")

                    # Verify & Respond
                    final_response = verifier.verify_and_respond(prompt, results)
                else:
                    final_response = "I couldn't generate a plan. Please try again."

            except Exception as e:
                logger.error(f"App Crash: {e}")
                final_response = f"An error occurred: {str(e)}"

        # Display Assistant Response
        with st.chat_message("assistant"):
            st.markdown(final_response)

        # Add Assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": final_response})

if __name__ == "__main__":
    main()
import os
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GroqClient:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model_name = model_name

    def generate_text(self, prompt: str) -> str:
        """
        Generates text using Llama 3.3 Versatile.
        Includes aggressive retry logic to handle '429 Resource Exhausted' errors.
        """
        max_retries = 3
        wait_time = 2  # Initial wait time in seconds

        for attempt in range(max_retries):
            try:
                # Call the API
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model_name,
                    temperature = 0.2
                )
                response_text = chat_completion.choices[0].message.content
                
                if not response_text:
                    raise ValueError("Empty response from Groq")

                return response_text

            except Exception as e:
                error_msg = str(e)
                # Check if it's a Rate Limit error (429)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print(f"\nGroq Rate Limit Hit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    wait_time *= 2 
                else:
                    # If it's a real crash (not just traffic), stop immediately
                    raise RuntimeError(f"Groq generation failed: {e}")
        
        raise RuntimeError("Max retries exceeded. The API is too busy right now.")

# Singleton instance
try:
    llm_client = GroqClient()
except Exception as e:
    print(f"Warning: Failed to initialize LLM Client. {e}")
    llm_client = None
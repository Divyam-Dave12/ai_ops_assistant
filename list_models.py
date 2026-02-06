import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("--- 🔍 SEARCHING FOR AVAILABLE MODELS ---")
try:
    # List all models available to your API key
    for model in client.models.list():
        # Print available attributes to inspect the model object
        print(f"Model attributes: {dir(model)}")
        print(f"✅ FOUND: {model.name}")
        # print(f"   - Display Name: {model.display_name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
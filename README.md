# 🎬 AI Movie Agent

A multi-agent AI system that acts as your personal movie expert. It can find movie titles from vague descriptions, fetch real-time metadata (ratings, directors, plot), provide YouTube trailers, and suggest streaming options.

Built with **Python**, **Streamlit**, and **Groq (LLM)**.

---

## 🚀 Features
- **Intelligent Search:** Can identify movies even from vague queries (e.g., "The movie where Brad Pitt ages backwards").
- **Multi-Agent Architecture:** Separates Planning, Execution, and Verification for robust error handling.
- **Smart Caching:** Remembers previous searches to avoid API rate limits and improve speed.
- **Context Awareness:** Remembers previous questions in the chat (e.g., "Who directed it?" works after finding a movie).
- **Resilient Fallbacks:** Gracefully handles missing data (e.g., finding a trailer even if OMDb details fail).

---

## 🛠️ Setup Instructions

Follow these steps to run the project locally on your machine.

### 1. Clone the Repository
```bash
git clone <YOUR_REPO_LINK_HERE>
cd ai_movie_agent
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: If you encounter issues with duckduckgo_search, ensure you are using the latest version via `pip install -U duckduckgo_search`)*

### 4. Configure Environment Variables
Create a file named `.env` in the root directory. You can copy the structure from `.env.example`:

```bash
# .env content
GROQ_API_KEY=your_groq_api_key_here
OMDB_API_KEY=your_omdb_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```
The app should open automatically in your browser at `http://localhost:8501`.

---

## 🔑 Environment Variables (.env.example)
Create a file named `.env.example` in your repository for reference:

```ini
# LLM Provider (Groq)
GROQ_API_KEY=

# Movie Metadata Provider
OMDB_API_KEY=

# Video Provider
YOUTUBE_API_KEY=
```

---

## 🏗️ Architecture
The system follows a Multi-Agent Pattern to ensure reliability:

1. **Planner Agent** (`agents/planner.py`):
   - Analyzes the user's request and chat history.
   - Breaks the request down into logical steps (e.g., Search -> Get Details -> Get Trailer).
   - Outputs a JSON execution plan.

2. **Executor Agent** (`agents/executor.py`):
   - Parses the JSON plan.
   - Calls specific tools (`tools/movie_tools.py`).
   - **Smart Context**: Passes the output of one step (e.g., a movie title found via search) into the next step automatically.
   - **Caching**: Checks `search_cache.json` before hitting external search APIs to reduce latency.

3. **Verifier Agent** (`agents/verifier.py`):
   - Consumes the raw data from the Executor.
   - Validates if the movie was actually found.
   - Generates a friendly, human-readable response using the LLM.

---

## 🔌 Integrated APIs
| Service | Purpose |
|---------|---------|
| **Groq (Llama 3)** | The "Brain" for planning, verifying, and extracting movie titles from search snippets. |
| **DuckDuckGo** | Performs web searches for vague queries (e.g., "Best sci-fi 2024"). |
| **OMDb API** | Fetches structured data: Release Year, IMDb Rating, Director, Plot. |
| **YouTube Data API** | Fetches the official trailer link. |

---

## 🧪 Example Prompts to Test
Try these prompts to see the agent's full capabilities:

- **The "Vague Description" Test:**
  > "What is the name of the movie where a car tire comes to life and kills people? I want to see the trailer."
  > *(Target: Rubber)*

- **The "Complex Award" Test:**
  > "Find the movie that won the Oscar for Best Animated Feature in 2024. Who directed it?"
  > *(Target: The Boy and the Heron)*

- **The "Series/Ambiguity" Test:**
  > "Find the trailer for the last Harry Potter movie released."
  > *(Target: Harry Potter and the Deathly Hallows – Part 2)*

- **The "Context Memory" Test:**
  > Turn 1: "Find the movie Inception."
  > Turn 2: "Who directed it?"

- **The "New Release" Test:**
  > "Find the trailer for the latest Mission Impossible movie coming out in 2025."

---

## ⚠️ Known Limitations & Tradeoffs
1. **DuckDuckGo Rate Limits:**
   - *Limitation:* The search library is aggressive and can be blocked by rate limits if used too rapidly.
   - *Mitigation:* We implemented a local JSON cache (`utils/cache.py`) to store successful searches. If blocked, the system relies on cached data.

2. **OMDb String Strictness:**
   - *Limitation:* OMDb requires exact title matches.
   - *Mitigation:* A regex cleaner handles common suffixes (e.g., " - IMDb") and we use the LLM to extract the exact title from search results before asking OMDb.

3. **Session Memory:**
   - *Limitation:* Streamlit reloads the script on every interaction.
   - *Mitigation:* Chat history is stored in `st.session_state` and passed back to the Planner on every turn to maintain context.

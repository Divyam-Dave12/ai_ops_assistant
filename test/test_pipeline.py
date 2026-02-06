import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent

class TestMovieAgent(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test."""
        # Mock the LLM client so we don't need a real Groq Key for CI
        self.mock_llm = MagicMock()
        self.planner = PlannerAgent()
        self.planner.llm = self.mock_llm # Inject mock
        
        self.executor = ExecutorAgent()

    def test_planner_logic(self):
        """Test if Planner can parse JSON correctly."""
        # Simulate LLM response
        fake_json_response = '''
        {
            "steps": [
                { "step_id": 1, "tool": "search_movie_details", "args": "Inception", "description": "Find movie" }
            ]
        }
        '''
        self.mock_llm.generate_text.return_value = fake_json_response
        
        plan = self.planner.create_plan("Find Inception", chat_history="")
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan["steps"][0]["tool"], "search_movie_details")
        self.assertEqual(plan["steps"][0]["args"], "Inception")

    @patch('agents.executor.search_movie_details')
    def test_executor_logic(self, mock_search):
        """Test if Executor runs tools correctly."""
        # Mock the actual tool execution
        mock_search.return_value = {"title": "Mock Movie", "year": "2024"}
        
        plan = {
            "steps": [
                { "step_id": 1, "tool": "search_movie_details", "args": "Mock Movie" }
            ]
        }
        
        results = self.executor.execute_plan(plan)
        
        self.assertIn("search_movie_details", results)
        self.assertEqual(results["search_movie_details"]["title"], "Mock Movie")

if __name__ == '__main__':
    unittest.main()
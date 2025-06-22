
import unittest
import os
from skills.llm_adapter import LLM

class TestLLMAdapter(unittest.TestCase):

    def test_gemini_provider(self):
        llm = LLM(provider="gemini")
        response = llm.chat(messages=[{"role": "user", "content": "Hello"}])
        self.assertIn("dummy response from Gemini", response)

    def test_openai_provider(self):
        llm = LLM(provider="openai")
        response = llm.chat(messages=[{"role": "user", "content": "Hello"}])
        self.assertIn("dummy response from OpenAI", response)

    def test_claude_provider(self):
        llm = LLM(provider="claude")
        response = llm.chat(messages=[{"role": "user", "content": "Hello"}])
        self.assertIn("dummy response from Claude", response)

    def test_unsupported_provider(self):
        llm = LLM(provider="unsupported")
        response = llm.chat(messages=[{"role": "user", "content": "Hello"}])
        self.assertIn("Unsupported LLM provider", response)

if __name__ == '__main__':
    unittest.main()



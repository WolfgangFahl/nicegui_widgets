"""
Created on 2023-06-21
Updated on 2025-11-16

@author: wf
"""

import unittest
from ngwidgets.basetest import Basetest
from ngwidgets.llm import LLM


class TestLLM(Basetest):
    """
    test LLM wrapper for standard OpenAI and OpenRouter support
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.llms = {}

        # 1. Standard OpenAI (uses OPENAI_API_KEY)
        self.llms["openai"] = LLM()

        # 2. OpenRouter (uses OPENROUTER_API_KEY)
        # We can use Claude or Google models here without extra dependencies
        self.llms["openrouter"] = LLM(
            base_url="https://openrouter.ai/api/v1",
            model="google/gemini-2.0-flash-001",  # or "anthropic/claude-3-haiku"
        )

    @unittest.skipIf(Basetest.inPublicCI(), "LLM tests with API cost")
    def testModelList(self):
        """
        Test listing models for configured providers
        """
        for name, llm in self.llms.items():
            if not llm.available():
                if self.debug:
                    print(f"{name} LLM not available - skipping model list")
                continue

            print(f"Listing models for {name} ...")
            try:
                models = llm.client.models.list()
                # OpenRouter returns a HUGE list, so limit debug output
                count = 0
                for model in models.data:
                    count += 1
                    if self.debug and count <= 5:
                        print(f"{name} model: {model.id}")
            except Exception as ex:
                if "401" in str(ex):
                    print(f"{name} auth failed (API Key missing or invalid).")
                else:
                    raise ex

    @unittest.skipIf(Basetest.inPublicCI(), "LLM tests with API costs")
    def testAsk(self):
        """
        Test simple Q&A
        """
        for name, llm in self.llms.items():
            if not llm.available():
                if self.debug:
                    print(f"{name} LLM not available - skipping ask")
                continue

            print(f"Asking {name} ({llm.model}) ...")
            try:
                result = llm.ask("Who was the first man on the moon?")
                if self.debug:
                    print(f"{name} Answer: {result}")
                self.assertTrue("Armstrong" in result)
            except Exception as ex:
                if any(x in str(ex).lower() for x in ["quota", "insufficient_quota", "401", "402"]):
                    print(f"{name}: quota/auth issue, skipping assertion.")
                else:
                    self.fail(f"{name} failed: {str(ex)}")
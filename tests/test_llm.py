"""
Created on 2023-06-21

@author: wf
"""

import unittest

from ngwidgets.basetest import Basetest
from ngwidgets.claude_llm import ClaudeLLM
from ngwidgets.llm import LLM


class TestLLM(Basetest):
    """
    test https://github.com/openai/openai-python library
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.llms = {"openai": LLM(), "claude": ClaudeLLM()}

    @unittest.skipIf(Basetest.inPublicCI(), "LLM tests with API cost")
    def testModelList(self):
        # list models
        for name, llm in self.llms.items():
            if name == "openai":
                models = llm.client.models.list()
                for model in models.data:
                    if self.debug:
                        print(model)
        pass

    @unittest.skipIf(Basetest.inPublicCI(), "LLM tests with API costs")
    def testAsk(self):
        """
        test the LLM interface
        """
        for name, llm in self.llms.items():
            if not llm.available():
                if self.debug:
                    print(f"{name} LLM not available - skipping")
                continue
            try:
                result = llm.ask("Who was the first man on the moon?")
                if self.debug:
                    print(f"{name}:{result}")
                self.assertTrue("Armstrong" in result)
            except Exception as ex:
                if "quota" in str(ex):
                    if self.debug:
                        print("ignoring quota issue")

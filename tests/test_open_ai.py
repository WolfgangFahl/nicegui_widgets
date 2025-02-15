"""
Created on 2023-06-21

@author: wf
"""

import unittest

from openai import OpenAI

from ngwidgets.basetest import Basetest
from ngwidgets.llm import LLM


class TestOpenAi(Basetest):
    """
    test https://github.com/openai/openai-python library
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.llm = LLM()

    @unittest.skipIf(Basetest.inPublicCI(), "chatgpt")
    def testOpenAI(self):
        # list models
        models = self.llm.client.models.list()
        for model in models.data:
            if self.debug:
                print(model)
        pass

    @unittest.skipIf(Basetest.inPublicCI(), "chatgpt")
    def testChatGpt(self):
        """
        test the chatgpt interface
        """
        result = self.llm.ask("Who was the first man on the moon?")
        debug = True
        if debug:
            print(result)
        self.assertTrue("Armstrong" in result)

"""
Created on 2023-06-21
Updated on 2025-11-26

@author: wf
"""

import unittest
from pathlib import Path

from ngwidgets.basetest import Basetest
from ngwidgets.llm import LLM, VisionLLM


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
        self.llms["openrouter"] = LLM(
            base_url="https://openrouter.ai/api/v1",
            model="google/gemini-2.0-flash-001",
        )

        # 3. Vision LLM
        self.vision_llm = VisionLLM(
            base_url="https://openrouter.ai/api/v1",
            model="google/gemini-2.0-flash-001",
        )

    def _call_llm(self, func, *args, **kwargs):
        """
        Execute LLM call and skip the test when the provider is not usable.

        Returns:
            the result of func, the test is skipped on an
            auth (401), payment (402), model not found (404) or quota (429) error
        """
        try:
            result = func(*args, **kwargs)
        except Exception as ex:
            msg = str(ex).lower()
            if any(
                x in msg
                for x in [
                    "quota",
                    "insufficient_quota",
                    "401",
                    "402",
                    "404",
                    "429",
                ]
            ):
                self.skipTest(f"LLM provider not usable: {str(ex)}")
            raise ex
        return result

    @unittest.skipIf(Basetest.inPublicCI(), "LLM tests with API cost")
    def testModelList(self):
        """
        Test listing models for configured providers
        """
        for name, llm in self.llms.items():
            if not llm.available():
                continue

            print(f"Listing models for {name} ...")
            models = self._call_llm(llm.client.models.list)

            if models:
                # OpenRouter returns a HUGE list, so limit debug output
                count = 0
                for model in models.data:
                    count += 1
                    if self.debug and count <= 5:
                        print(f"{name} model: {model.id}")

    @unittest.skipIf(Basetest.inPublicCI(), "LLM tests with API costs")
    def testAsk(self):
        """
        Test simple Q&A
        """
        for name, llm in self.llms.items():
            if not llm.available():
                continue

            print(f"Asking {name} ({llm.model}) ...")
            result = self._call_llm(llm.ask, "Who was the first man on the moon?")

            if result:
                if self.debug:
                    print(f"{name} Answer: {result}")
                self.assertTrue("Armstrong" in result)

    @unittest.skipIf(Basetest.inPublicCI(), "LLM tests with API costs")
    def testVisionAnalysis(self):
        """
        Test vision capabilities using existing resources.
        """
        if not self.vision_llm.available():
            return

        # Use the specific resource file
        image_path = Path(__file__).parent / "resources" / "ALDI-WarrantyCard.jpg"

        self.assertTrue(image_path.exists(), f"Test image not found at {image_path}")

        print(f"Testing Vision ({self.vision_llm.model}) with: {image_path}")

        # 2. Execute via helper
        prompt = "Extract the store brand, the product name, and the Article Number (Artikelnummer) from this image."
        result = self._call_llm(self.vision_llm.analyze_image, str(image_path), prompt)

        # 3. Assert if we got a result
        if result:
            if self.debug:
                print(f"Vision Result: {result}")

            self.assertTrue("ALDI" in result.upper())
            self.assertTrue("SENSOR" in result.upper())
            self.assertTrue("709433" in result)

"""
Created on 2025-12-08

@author: wf
"""

"""
UTF-8 based histogram class.
"""

import math
from collections import Counter
from typing import Any, Dict, List, Union

from basemkit.basetest import Basetest
from ngwidgets.llm import LLM
from ngwidgets.ai_tasks import AITasks, ModelConfig, TaskConfig


class Utf8Histogram:
    """
    Class for creating and printing UTF-8 text-based histograms.
    Supports categorical (dict) and numeric (list with binning) data.
    """

    # Fractional blocks for smoother bars: 1/8 to 8/8
    _BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

    def __init__(self, data: Dict[str, Union[int, float]], title: str, width: int = 75):
        self.title = title
        self.data = data
        self.width = width

    @classmethod
    def from_objects_list(
        cls,
        object_list: List[Any],
        title: str,
        key_func: callable,
        is_numeric: bool = False,
        rows: int = 10,
    ) -> "Utf8Histogram":
        """
        Factory method to extract values from a list of objects using a key function
        """
        items = [val for o in object_list if (val := key_func(o)) is not None]
        if is_numeric:
            histogram = cls.from_numeric(title=title, values=items, bins=rows)
        else:
            histogram = cls.from_counts(title=title, items=items, top_n=rows)
        return histogram

    @classmethod
    def from_counts(
        cls, items: List[Any], title: str, top_n: int = 20
    ) -> "Utf8Histogram":
        """Creates a chart from categorical data (frequency count)."""
        if not items:
            return cls({}, title)
        counts = Counter(items)
        # Sort by count desc, then alphabetically
        data = dict(sorted(counts.most_common(top_n), key=lambda x: (-x[1], x[0])))
        return cls(data, f"{title} (Top {len(data)})")

    @classmethod
    def from_numeric(
        cls, values: List[Union[int, float]], title: str, bins: int = 10
    ) -> "Utf8Histogram":
        """Creates a histogram by binning numeric data."""
        if not values:
            return cls({}, title)

        mn, mx = min(values), max(values)
        if mn == mx:
            mx += 1  # Avoid division by zero

        step = (mx - mn) / bins
        buckets = [0] * bins
        labels = []

        # Generate labels
        for i in range(bins):
            start, end = mn + (i * step), mn + ((i + 1) * step)
            # Format labels: integer if numbers are large (>20), else float
            if mx > 20:
                lbl_fmt = f"{int(start)}-{int(end)}"
            else:
                lbl_fmt = f"{start:.2f}-{end:.2f}"
            labels.append(lbl_fmt)

        # Fill buckets
        for val in values:
            if val is None:
                continue
            # Calculate index based on distance from min
            idx = int((val - mn) / step)
            # Clamp to max bucket index (handles the exact max value case)
            buckets[min(idx, bins - 1)] += 1

        return cls(dict(zip(labels, buckets)), f"{title} (n={len(values)})")

    def _make_bar(self, val: float, max_val: float) -> str:
        """Calculates full blocks + fractional remainder."""
        if max_val == 0:
            return ""

        total_len = (val / max_val) * self.width
        full_blocks = int(total_len)
        remainder = total_len - full_blocks

        frac_idx = int(remainder * 8)
        return (self._BLOCKS[-1] * full_blocks) + (
            self._BLOCKS[frac_idx] if full_blocks < self.width else ""
        )

    def render(self) -> None:
        """Prints the chart to stdout."""
        print(f"\n{self.title}\n{'=' * len(self.title)}")

        if not self.data:
            print("No data available.")
            return

        max_val = max(self.data.values()) if self.data else 1
        # Dynamic label width
        label_width = max((len(str(k)) for k in self.data.keys()), default=10)

        for label, value in self.data.items():
            bar = self._make_bar(value, max_val)
            print(f"{label:<{label_width}} ▐ {bar} {value}")
        print()


class TestAITasks(Basetest):
    """
    test the ai tasks handling
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.ai_tasks = AITasks.get_instance()

    def test_load_ai_tasks(self):
        """
        Test loading AI tasks from YAML file
        """
        ai_tasks = self.ai_tasks
        if self.debug:
            ai_yaml = ai_tasks.to_yaml()
            print(f"\nLoaded AI Configuration: {ai_yaml}")

        self.assertIsNotNone(ai_tasks.tasks)
        self.assertIsInstance(ai_tasks.tasks, dict)
        self.assertGreater(len(ai_tasks.tasks), 0, "No tasks loaded")

        # Check for specific expected task (ocr4wiki)
        self.assertIn("ocr4business", ai_tasks.tasks, "ocr4business task not found")
        ocr_task = ai_tasks.tasks["ocr4business"]
        self.assertIsInstance(ocr_task, TaskConfig)
        self.assertIsNotNone(ocr_task.prompt)
        self.assertIn("OCR", ocr_task.prompt, "OCR not in prompt")
        self.assertIn("OCR-Extractor with Summary", ocr_task.description)

    def testModels(self):
        """
        test different models
        """
        llm = LLM(base_url=self.ai_tasks.api.base_url)
        # in public CI this might happen
        if not llm.client:
            return
        models = llm.client.models.list()
        configs = []
        for i, model in enumerate(models):
            model_config = ModelConfig.from_openai_model(model)
            if self.debug:
                print(f"{i}: {model_config}")
            if (
                model_config.price_per_mtoken
                and model_config.price_per_mtoken < 1
                and model_config.context_length > 100000
            ):
                configs.append(model_config)

        # Top Providers (categorical)
        Utf8Histogram.from_objects_list(
            object_list=configs,
            title="Top Model Providers",
            key_func=lambda o: o.provider,
            is_numeric=False,
            rows=15,
        ).render()

        # context length
        Utf8Histogram.from_objects_list(
            object_list=configs,
            title="log 2 of Context length",
            key_func=lambda o: math.log2(o.context_length),
            is_numeric=True,
            rows=20,
        ).render()

        # Price Distribution (numeric with binning)
        Utf8Histogram.from_objects_list(
            object_list=configs,
            title="Price Distribution ($ per Million Tokens)",
            key_func=lambda o: o.price_per_mtoken,
            is_numeric=True,
            rows=20,
        ).render()

        # input_types
        Utf8Histogram.from_objects_list(
            object_list=configs,
            title="input types",
            key_func=lambda o: str(o.input_types),
            rows=20,
        ).render()

        for model_config in configs:
            if "image" in model_config.input_types:
                print(model_config.to_yaml())

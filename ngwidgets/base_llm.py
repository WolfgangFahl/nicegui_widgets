"""
Created on 2025-04-07

@author: wf
"""

import time
from dataclasses import field
from datetime import datetime
from typing import List, Optional

from basemkit.yamlable import lod_storable


@lod_storable
class Prompt:
    """
    a single prompt with response
    """

    prompt: str
    response: str
    tokens: int
    temperature: float
    timestamp: datetime
    duration: float
    model: Optional[str] = None
    model_details: Optional[str] = None
    image_path: Optional[str] = None

    def append_to_file(self, filepath: str):
        # Open the file in append mode
        with open(filepath, "a") as file:
            # Dump the new prompt as YAML directly into the file
            yaml_str = self.to_yaml()
            # Ensure the new prompt starts on a new line
            file.write(f"\n{yaml_str}")

    @classmethod
    def from_chat(
        self,
        prompt_text: str,
        result: str,
        chat_completion,
        start_time: datetime,
        model: Optional[str] = None,
        image_path: Optional[str] = None,
        temperature: float = 0.7,
    ) -> "Prompt":
        """
        Create a prompt instance with timing and usage info
        """
        total_tokens = chat_completion.usage.total_tokens
        model_details = chat_completion.model
        duration = (datetime.now() - start_time).total_seconds()
        prompt = Prompt(
            prompt=prompt_text,
            response=result,
            model=model,
            model_details=model_details,
            temperature=temperature,
            tokens=total_tokens,
            timestamp=datetime.now(),
            duration=duration,
            image_path=image_path,
        )
        return prompt


@lod_storable
class Prompts:
    """
    keep track of a series of prompts
    """

    prompts: List[Prompt] = field(default_factory=list)

    def add_to_filepath(
        self, new_prompt: Prompt, prompts_filepath, debug: bool = False
    ):
        start_save_time = time.time()

        # Save the prompts to a file
        self.prompts.append(new_prompt)
        new_prompt.append_to_file(prompts_filepath)

        # After saving
        end_save_time = time.time()
        save_duration = end_save_time - start_save_time
        if debug:
            print(f"Time taken to append to prompts: {save_duration} seconds")


class BaseLLM:
    """
    Large Language Model access wrapper
    """

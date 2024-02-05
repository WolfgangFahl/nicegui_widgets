"""
Created on 2023-06-23

@author: wf
"""
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import openai

from ngwidgets.yamlable import lod_storable


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

    def append_to_file(self, filepath: str):
        # Open the file in append mode
        with open(filepath, "a") as file:
            # Dump the new prompt as YAML directly into the file
            yaml_str = self.to_yaml()
            # Ensure the new prompt starts on a new line
            file.write(f"\n{yaml_str}")


@lod_storable
class Prompts:
    """
    keep track of a series of prompts
    """

    prompts: List[Prompt] = field(default_factory=list)


class LLM:
    """
    Large Language Model access wrapper
    """

    # Define a dictionary that maps models to their size limits
    MODEL_SIZE_LIMITS = {
        "gpt-3.5-turbo": 4096,  # Adjust this limit as needed for other models
        "gpt-3.5-turbo-16k": 4096 * 4,
    }

    # Define a constant for the average token character length
    AVERAGE_TOKEN_CHAR_LEN = 4  # Adjust this value based on the model
    DEFAULT_MODEL = "gpt-3.5-turbo"

    def __init__(
        self,
        api_key: str = None,
        model=DEFAULT_MODEL,
        force_key: bool = False,
        prompts_filepath: str = None,
    ):
        """
        constructor

        Args:
            api_key(str): the access key
            model(str): the model to use
            prompt_filepath(str): the filepath for the prompt logging
        """
        self.model = model
        self.token_size_limit = LLM.MODEL_SIZE_LIMITS.get(
            model, 4096
        )  # Default to 4096 if model not found
        self.char_size_limit = self.token_size_limit * LLM.AVERAGE_TOKEN_CHAR_LEN
        openai_api_key = None
        if api_key:
            # If an API key is provided during object creation, set it.
            openai.api_key = api_key
        else:
            # Load the API key from the environment or a JSON file
            openai_api_key = os.getenv("OPENAI_API_KEY")
            json_file = Path.home() / ".openai" / "openai_api_key.json"

            if openai_api_key is None and json_file.is_file():
                with open(json_file, "r") as file:
                    data = json.load(file)
                    openai_api_key = data.get("OPENAI_API_KEY")

        if openai_api_key is None:
            if force_key:
                raise ValueError(
                    "No OpenAI API key found. Please set the 'OPENAI_API_KEY' environment variable or store it in `~/.openai/openai_api_key.json`."
                )
            else:
                return
        # set the global api key
        openai.api_key = openai_api_key
        # If prompts_filepath is None, use default path in the user's home directory with the current date
        if prompts_filepath is None:
            # Format: Year-Month-Day
            date_str = datetime.now().strftime("%Y-%m-%d")
            default_filename = f"prompts_{date_str}.yaml"  # Constructs the file name
            openai_dir = (
                Path.home() / ".openai"
            )  # Constructs the path to the .openai directory

            # Check if .openai directory exists, create if it doesn't
            if not openai_dir.exists():
                openai_dir.mkdir(parents=True, exist_ok=True)

            prompts_filepath = openai_dir / default_filename  # Constructs the full path

        self.prompts_filepath = prompts_filepath

        # Load or initialize the prompts file
        if prompts_filepath.is_file():
            self.prompts = Prompts.load_from_yaml_file(str(prompts_filepath))
        else:
            # If the file doesn't exist, create an empty Prompts object
            # You might want to handle directory creation here if .openai directory might not exist
            self.prompts = Prompts()

    def available(self):
        """
        check availability of API by making sure there is an api_key

        Returns:
            bool: True if the Large Language Model is available
        """
        return openai.api_key is not None

    def ask(self, prompt_text: str, model: str = None, temperature: float = 0.7) -> str:
        """
        ask a prompt

        Args:
            prompt_text(str): The text of the prompt to send to the model.
            model(str): the model to use - if None self.model is used
            temperature(float): Controls randomness in the response. Lower is more deterministic.
        Returns:
            str: the answer
        """
        if len(prompt_text) > self.char_size_limit:
            raise ValueError(
                f"Prompt exceeds size limit of {self.char_size_limit} characters."
            )
        if model is None:
            model = self.model

        # Start timing the response
        start_time = datetime.now()

        # Interact with the API
        chat_completion = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=temperature,  # Include the temperature parameter here
        )
        result = chat_completion.choices[0].message.content
        total_tokens = chat_completion.usage.total_tokens
        model_details = chat_completion.get("model")

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Create a new Prompt instance and append it to the prompts list
        new_prompt = Prompt(
            prompt=prompt_text,
            response=result,
            model=model,
            model_details=model_details,
            temperature=temperature,
            tokens=total_tokens,
            timestamp=datetime.now(),
            duration=duration,
        )
        start_save_time = time.time()

        # Save the prompts to a file
        self.prompts.prompts.append(new_prompt)
        new_prompt.append_to_file(self.prompts_filepath)

        # After saving
        end_save_time = time.time()
        save_duration = end_save_time - start_save_time
        print(f"Time taken to append to prompts: {save_duration} seconds")
        return result

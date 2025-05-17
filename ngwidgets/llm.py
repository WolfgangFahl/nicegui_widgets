"""
Created on 2023-06-23

@author: wf
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from openai import OpenAI

from ngwidgets.base_llm import BaseLLM, Prompt, Prompts


class LLM(BaseLLM):
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
        self.client = None
        self.model = model
        self.token_size_limit = LLM.MODEL_SIZE_LIMITS.get(
            model, 4096
        )  # Default to 4096 if model not found
        self.char_size_limit = self.token_size_limit * LLM.AVERAGE_TOKEN_CHAR_LEN
        openai_api_key = None
        if api_key:
            # If an API key is provided during object creation, set it.
            openai_api_key = api_key
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
        # set the client using the  api key
        self.client = OpenAI(api_key=openai_api_key)
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
        return self.client is not None

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
        chat_completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=temperature,  # Include the temperature parameter here
        )
        result = chat_completion.choices[0].message.content
        new_prompt = Prompt.from_chat(
            prompt_text,
            result,
            chat_completion,
            start_time,
            model,
            temperature=temperature,
        )
        self.prompts.add_to_filepath(new_prompt, self.prompts_filepath)
        return result


class VisionLLM(LLM):
    """
    Extension of LLM class to handle image analysis
    """

    def __init__(
        self, api_key: str = None, model="gpt-4o-mini", force_key: bool = False
    ):
        """
        Initialize with vision model as default
        """
        super().__init__(api_key=api_key, model=model, force_key=force_key)

    def analyze_image(self, image_path: str, auth: dict, prompt_text: str) -> str:
        """
        Analyze an image with a given prompt

        Args:
            image_path: Path to local file or URL of the image
            prompt_text: The text prompt to guide the image analysis

        Returns:
            str: The model's response
        """
        start_time = datetime.now()
        if image_path.startswith("http"):
            if auth:
                # Insert auth info into URL if present
                url_parts = image_path.split("://", 1)
                image_url = f"{url_parts[0]}://{auth['username']}:{auth['password']}@{url_parts[1]}"
            else:
                image_url = image_path
            image_content = {"type": "image_url", "image_url": {"url": image_url}}
        else:
            # Local file - use base64
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                }

        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt_text}, image_content],
            }
        ]

        chat_completion = self.client.chat.completions.create(
            model=self.model, messages=messages
        )

        result = chat_completion.choices[0].message.content
        new_prompt = Prompt.from_chat(
            prompt_text,
            result,
            chat_completion,
            start_time,
            self.model,
            image_path=image_path,
        )
        self.prompts.add_to_filepath(new_prompt, self.prompts_filepath)

        return result

"""
Created on 2025-04-07

@author: wf
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path

import anthropic

from ngwidgets.base_llm import BaseLLM, Prompt, Prompts


class ClaudeLLM(BaseLLM):
    """
    Claude Large Language Model access wrapper

    to get a key visit
    https://console.anthropic.com/
    """

    # Define a dictionary that maps models to their token limits
    MODEL_SIZE_LIMITS = {
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
        "claude-3.5-sonnet-20240620": 200000,
        "claude-3.7-sonnet-20250219": 200000,
    }

    # Default model
    DEFAULT_MODEL = "claude-3.7-sonnet-20250219"

    def __init__(
        self,
        api_key=None,
        model=DEFAULT_MODEL,
        force_key=False,
        prompts_filepath=None,
        max_tokens=4000,
    ):
        """
        constructor

        Args:
            api_key: The access key for Claude API
            model: The model name to use
            force_key: If True, raise error when key is missing
            prompts_filepath: Path for storing prompt history
            max_tokens: Maximum tokens in the response
        """
        self.client = None
        self.model = model
        self.max_tokens = max_tokens
        self.token_size_limit = self.MODEL_SIZE_LIMITS.get(model, 200000)

        # Get API key from environment or file
        anthropic_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # Try to load from JSON file if not provided
        if not anthropic_api_key:
            json_file = Path.home() / ".anthropic" / "anthropic_api_key.json"
            if json_file.is_file():
                with open(json_file, "r") as file:
                    data = json.load(file)
                    anthropic_api_key = data.get("ANTHROPIC_API_KEY")

        # Initialize client if key is available
        if anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        elif force_key:
            raise ValueError(
                "No Anthropic API key found. Please set the 'ANTHROPIC_API_KEY' environment variable or store it in `~/.anthropic/anthropic_api_key.json`."
            )

        # Set up prompts filepath
        if prompts_filepath is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            default_filename = f"claude_prompts_{date_str}.yaml"
            anthropic_dir = Path.home() / ".anthropic"

            if not anthropic_dir.exists():
                anthropic_dir.mkdir(parents=True, exist_ok=True)

            prompts_filepath = anthropic_dir / default_filename

        self.prompts_filepath = prompts_filepath

        # Initialize prompts
        if os.path.isfile(prompts_filepath):
            self.prompts = Prompts.load_from_yaml_file(str(prompts_filepath))
        else:
            self.prompts = Prompts()

    def available(self):
        """
        check availability of API by making sure there is an api_key

        Returns:
            bool: True if the API client is available
        """
        return self.client is not None

    def ask(self, prompt_text, model=None, temperature=0.7, system_prompt=None):
        """
        ask a prompt

        Args:
            prompt_text: The text of the prompt to send to the model
            model: The model to use (defaults to self.model)
            temperature: Controls randomness in the response
            system_prompt: Optional system prompt for context

        Returns:
            str: The model's response
        """
        if not self.available():
            return "Claude API not available"

        if model is None:
            model = self.model

        # Start timing
        start_time = datetime.now()

        # Prepare message for Claude API
        message_kwargs = {
            "model": model,
            "max_tokens": self.max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt_text}],
        }

        # Add system prompt if provided
        if system_prompt:
            message_kwargs["system"] = system_prompt

        # Call Claude API
        message_completion = self.client.messages.create(**message_kwargs)

        # Extract response text
        result = message_completion.content[0].text

        # Create and save prompt record
        new_prompt = Prompt.from_chat(
            prompt_text,
            result,
            message_completion,
            start_time,
            model,
            temperature=temperature,
        )
        self.prompts.add_to_filepath(new_prompt, self.prompts_filepath)

        return result


class ClaudeVisionLLM(ClaudeLLM):
    """
    Extension of ClaudeLLM class to handle image analysis
    """

    def __init__(self, api_key=None, model="claude-3-opus-20240229", force_key=False):
        """
        Initialize with vision-capable model as default

        Args:
            api_key: The access key for Claude API
            model: The model name to use (should be vision-capable)
            force_key: If True, raise error when key is missing
        """
        super().__init__(api_key=api_key, model=model, force_key=force_key)

    def analyze_image(self, image_path, prompt_text, system_prompt=None):
        """
        Analyze an image with a given prompt

        Args:
            image_path: Path to local file or URL of the image
            prompt_text: The text prompt to guide the image analysis
            system_prompt: Optional system prompt for context

        Returns:
            str: The model's response
        """
        if not self.available():
            return "Claude Vision API not available"

        # Start timing
        start_time = datetime.now()

        # Prepare media content based on image source
        if image_path.startswith("http"):
            media_content = {
                "type": "image",
                "source": {"type": "url", "url": image_path},
            }
        else:
            # Handle local file
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                media_content = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": self._get_media_type(image_path),
                        "data": base64.b64encode(image_data).decode("utf-8"),
                    },
                }

        # Construct message with text and image content
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt_text}, media_content],
            }
        ]

        # Prepare API call parameters
        message_kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }

        # Add system prompt if provided
        if system_prompt:
            message_kwargs["system"] = system_prompt

        # Create the message
        message_completion = self.client.messages.create(**message_kwargs)

        # Extract response text
        result = message_completion.content[0].text

        # Create and save prompt record
        new_prompt = Prompt.from_chat(
            prompt_text,
            result,
            message_completion,
            start_time,
            self.model,
            image_path=image_path,
        )
        self.prompts.add_to_filepath(new_prompt, self.prompts_filepath)

        return result

    def _get_media_type(self, image_path):
        """
        Determine the media type (MIME type) based on file extension

        Args:
            image_path: Path to the image file

        Returns:
            str: MIME type of the image
        """
        extension = image_path.lower().split(".")[-1]

        mime_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
            "svg": "image/svg+xml",
            "heic": "image/heic",
        }

        return mime_types.get(extension, "application/octet-stream")

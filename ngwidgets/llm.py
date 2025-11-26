"""
Created on 2023-06-23
Updated on 2025-11-26 to support openrouter and clean up structure

@author: wf
"""
import base64
import json
import os
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from ngwidgets.base_llm import BaseLLM, Prompt, Prompts


class LLM(BaseLLM):
    """
    Large Language Model access wrapper via openai-python library.
    Supports OpenAI and OpenRouter (via base_url).
    """

    # Define a dictionary that maps models to their size limits
    MODEL_SIZE_LIMITS = {
        "gpt-3.5-turbo": 4096,
        "gpt-4o-mini": 128000,
        "google/gemini-2.0-flash-001": 1000000,
        "anthropic/claude-3.5-sonnet": 200000,
    }

    # Define a constant for the average token character length
    AVERAGE_TOKEN_CHAR_LEN = 4
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(
        self,
        api_key: str = None,
        model: str = DEFAULT_MODEL,
        force_key: bool = False,
        prompts_filepath: str = None,
        base_url: str = None,
    ):
        """
        constructor

        Args:
            api_key(str): the access key
            model(str): the model to use
            force_key(bool): if True, raise ValueError if no key is available
            prompts_filepath(str): the filepath for the prompt logging
            base_url(str): custom base URL (e.g. https://openrouter.ai/api/v1)
        """
        self.client = None
        self.model = model
        self.token_size_limit = LLM.MODEL_SIZE_LIMITS.get(model, 4096)
        self.char_size_limit = self.token_size_limit * LLM.AVERAGE_TOKEN_CHAR_LEN
        self.base_url = base_url

        # Resolve API Key
        self.api_key = self.get_api_key(api_key)

        if self.api_key is None:
            if force_key:
                raise ValueError(
                    "No API key found. Please set 'OPENAI_API_KEY' (or 'OPENROUTER_API_KEY') or check config files."
                )
            else:
                return

        # Initialize Client
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        # Setup Prompts Logging
        self.prompts_filepath = self._get_prompts_filepath(prompts_filepath)

        if self.prompts_filepath and self.prompts_filepath.is_file():
            self.prompts = Prompts.load_from_yaml_file(str(self.prompts_filepath)) # @UndefinedVariable
        else:
            self.prompts = Prompts()

    def _is_openrouter(self) -> bool:
        """Check if current configuration is pointing to OpenRouter"""
        return self.base_url and "openrouter" in self.base_url

    def get_api_key(self, api_key: str) -> str:
        """
        Resolve the API key from arguments, environment variables, or configuration files.
        Prioritizes OpenRouter sources if base_url indicates OpenRouter usage.
        """
        if api_key:
            return api_key

        if self._is_openrouter():
            return self._get_openrouter_key()

        return self._get_openai_key()

    def _get_openrouter_key(self) -> str:
        """
        Retrieve OpenRouter API key from environment or config file.
        """
        # Check Env
        key = os.getenv("OPENROUTER_API_KEY")
        if key:
            return key

        # Check File
        key_file = Path.home() / ".openrouter" / "apikey.txt"
        if key_file.is_file():
            return key_file.read_text().strip()

        return None

    def _get_openai_key(self) -> str:
        """
        Retrieve Standard OpenAI API key from environment or config file.
        """
        # Check Env
        key = os.getenv("OPENAI_API_KEY")
        if key:
            return key

        # Check File
        json_file = Path.home() / ".openai" / "openai_api_key.json"
        if json_file.is_file():
            try:
                with open(json_file, "r") as file:
                    data = json.load(file)
                    return data.get("OPENAI_API_KEY")
            except Exception:
                pass
        return None

    def _get_prompts_filepath(self, filepath_arg: str) -> Path:
        """
        Determine the file path for logging prompts.
        """
        if filepath_arg:
            return Path(filepath_arg)

        date_str = datetime.now().strftime("%Y-%m-%d")
        default_filename = f"prompts_{date_str}.yaml"
        openai_dir = Path.home() / ".openai"
        if not openai_dir.exists():
            openai_dir.mkdir(parents=True, exist_ok=True)
        return openai_dir / default_filename

    def _get_extra_headers(self) -> dict:
        """Get extra headers for OpenRouter if applicable"""
        if self._is_openrouter():
            return {
                "HTTP-Referer": "https://github.com/WolfgangFahl/ngwidgets",
                "X-Title": "ngwidgets",
            }
        return None

    def available(self):
        """
        check availability of API by making sure there is an api_key
        """
        return self.client is not None

    def ask(self, prompt_text: str, model: str = None, temperature: float = 0.7) -> str:
        """
        ask a prompt
        """
        if len(prompt_text) > self.char_size_limit:
            raise ValueError(
                f"Prompt exceeds size limit of {self.char_size_limit} characters."
            )
        if model is None:
            model = self.model

        start_time = datetime.now()

        chat_completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=temperature,
            extra_headers=self._get_extra_headers(),
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
        self,
        api_key: str = None,
        model="gpt-4o-mini",
        force_key: bool = False,
        base_url: str = None,
    ):
        super().__init__(
            api_key=api_key, model=model, force_key=force_key, base_url=base_url
        )

    def analyze_image(
        self, image_path: str, prompt_text: str, auth: dict = None
    ) -> str:
        """
        Analyze an image with a given prompt
        """
        start_time = datetime.now()
        if image_path.startswith("http"):
            if auth:
                url_parts = image_path.split("://", 1)
                image_url = f"{url_parts[0]}://{auth['username']}:{auth['password']}@{url_parts[1]}"
            else:
                image_url = image_path
            image_content = {"type": "image_url", "image_url": {"url": image_url}}
        else:
            if not os.path.exists(image_path):
                return f"Error: Image path '{image_path}' does not exist."

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
            model=self.model,
            messages=messages,
            extra_headers=self._get_extra_headers(),
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
"""
Created on 2025-12-08

@author: wf
"""

from dataclasses import field
from pathlib import Path
from typing import Dict, List, Optional, Any

from basemkit.yamlable import lod_storable
from ngwidgets.llm import LLM, VisionLLM


@lod_storable
class APIConfig:
    """API configuration for LLM services"""

    base_url: str = "https://openrouter.ai/api/v1"  # The endpoint URL for the LLM API provider


@lod_storable
class ModelConfig:
    """Configuration for an LLM model"""

    name: str  # Full OpenRouter model ID (e.g., google/gemini-2.0-flash-001)
    provider: str  # The model provider organization (e.g., google, openai, anthropic)
    description: Optional[str] = None  # A human-readable summary of the model's capabilities
    context_length: Optional[int] = None  # Maximum context window size in tokens
    price_per_mtoken: Optional[float] = None  # cost per million tokens in USD
    input_types: List[str] = field(
        default_factory=lambda: ["text"]
    )  # List of supported modalities (e.g., ["text", "vision"])

    @classmethod
    def from_openai_model(cls, model: Any) -> "ModelConfig":
        """
        Create ModelConfig from an OpenAI API model object.

        The price per million tokens is calculated as the average of input and output costs:
        $$ P_{avg} = \frac{P_{prompt} + P_{completion}}{2} \times 1,000,000 $$
        """
        # Extract provider from model ID
        provider = model.id.split("/")[0] if "/" in model.id else "unknown"

        # Calculate price per million tokens (average of prompt + completion)
        price_per_mtoken = None
        pricing = getattr(model, "pricing", None)
        if pricing:
            avg_price = (float(pricing["prompt"]) + float(pricing["completion"])) / 2
            if avg_price > 0:
                price_per_mtoken = avg_price * 1_000_000

        # Determine input types from architecture modalities
        input_types = ["text"]  # Text is universally supported
        arch = getattr(model, "architecture", {})
        modalities = arch.get("input_modalities", [])

        for modality in modalities:
            if modality in ["image", "audio", "video"] and modality not in input_types:
                input_types.append(modality)

        config_instance = cls(
            name=model.id,
            provider=provider,
            context_length=getattr(model, "context_length", None),
            price_per_mtoken=price_per_mtoken,
            input_types=input_types,
        )
        return config_instance


@lod_storable
class TaskConfig:
    """Configuration for an AI task"""

    prompt: str  # The system or user prompt template to send to the model
    model: Optional[str] = None  # Key reference to a specific entry in the models dictionary
    description: Optional[str] = None  # Description of what this specific task achieves
    input_type: str = "text"  # The required input modality (e.g., 'text', 'vision')


@lod_storable
class AITasks:
    """Complete AI configuration managing APIs, Models, and Tasks"""

    api: APIConfig = field(default_factory=APIConfig)  # General API connection settings
    models: Dict[str, ModelConfig] = field(
        default_factory=dict
    )  # Dictionary of available models, keyed by a short alias
    tasks: Dict[str, TaskConfig] = field(
        default_factory=dict
    )  # Dictionary of defined tasks, keyed by task name
    _instance: Optional["AITasks"] = None  # Singleton instance storage
    _llms: Dict[str, LLM] = field(
        default_factory=dict
    )  # Runtime cache of instantiated LLM clients

    @classmethod
    def get_instance(cls, yaml_file_path: Optional[str] = None) -> "AITasks":
        """Retrieve or create singleton instance"""
        if cls._instance is None:
            if yaml_file_path is None:
                examples_path = Path(__file__).parent.parent / "ngwidgets_examples"
                yaml_file_path = str(examples_path / "ai_tasks.yaml")

            # basemkit lod_storable load method
            cls._instance = cls.load_from_yaml_file(yaml_file_path)

        return cls._instance

    def perform_task(
        self,
        task_name: str,
        model_name: Optional[str] = None,
        prompt_override: Optional[str] = None,
        params:Dict[str,Any]=None,
    ) -> str:
        """
        Execute a configured AI task.

        Args:
            task_name: Key of the task in configuration.
            model_name: Optional override for the model key.
            prompt_override: Optional override for the prompt text.
            params: Additional parameters (e.g., image_path).

        Returns:
            str: The response text from the LLM.
        """
        if params is None:
            params = {}

        response: str = ""

        # 1. Validate task existence
        if task_name not in self.tasks:
            available = ", ".join(self.tasks.keys())
            raise ValueError(f"Unknown task '{task_name}'. Available: {available}")

        task = self.tasks[task_name]

        # 2. Determine target model
        target_model_name = model_name if model_name is not None else task.model
        if target_model_name is None:
            raise ValueError(f"No model specified for task '{task_name}'")

        # 3. Validate model existence
        if target_model_name not in self.models:
            available = ", ".join(self.models.keys())
            raise ValueError(f"Unknown model '{target_model_name}'. Available: {available}")

        model = self.models[target_model_name]

        # 4. Verify model supports the required input type
        if task.input_type not in model.input_types:
            supported = ", ".join(model.input_types)
            raise ValueError(
                f"Model '{target_model_name}' does not support input type '{task.input_type}'. "
                f"Supported types: {supported}"
            )

        # 5. Retrieve or Initialize LLM instance
        llm_cache_key = f"{target_model_name}-{task.input_type}"

        if llm_cache_key not in self._llms:
            if task.input_type == "vision":
                self._llms[llm_cache_key] = VisionLLM(
                    model=model.name,
                    base_url=self.api.base_url,
                )
            else:
                self._llms[llm_cache_key] = LLM(
                    model=model.name,
                    base_url=self.api.base_url,
                )

        llm = self._llms[llm_cache_key]

        # 6. Execute request
        prompt_text = prompt_override if prompt_override is not None else task.prompt

        if task.input_type == "vision":
            if "image_path" not in params:
                raise ValueError(
                    f"Vision task '{task_name}' requires 'image_path' parameter"
                )
            response = llm.analyze_image(
                image_path=params["image_path"], prompt_text=prompt_text
            )
        else:
            response = llm.ask(prompt=prompt_text, model=model.name)

        return response
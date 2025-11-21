"""LLM wrapper supporting both Claude and local Hugging Face models."""

import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

# Always import Claude and base LangChain (lightweight)
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

# HuggingFace imports are lazy-loaded only when needed
# This avoids loading torch/transformers when using Claude only

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available model types."""
    CLAUDE = "claude"
    HUGGINGFACE = "huggingface"


class HuggingFaceChatWrapper(BaseChatModel):
    """Wrapper to make HuggingFace models compatible with LangChain chat interface."""
    
    pipeline: Any  # TextGenerationPipeline (lazy-loaded)
    model_name: str
    max_new_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    
    class Config:
        arbitrary_types_allowed = True
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate response from messages."""
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)
        
        # Generate
        response = self.pipeline(
            prompt,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True,
            pad_token_id=self.pipeline.tokenizer.eos_token_id,
            **kwargs
        )[0]['generated_text']
        
        # Extract only the new generated text (remove the prompt)
        generated_text = response[len(prompt):].strip()
        
        # Create ChatGeneration
        message = AIMessage(content=generated_text)
        generation = ChatGeneration(message=message)
        
        return ChatResult(generations=[generation])
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a prompt string."""
        prompt_parts = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                prompt_parts.append(f"System: {message.content}\n")
            elif isinstance(message, HumanMessage):
                prompt_parts.append(f"User: {message.content}\n")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}\n")
            else:
                prompt_parts.append(f"{message.content}\n")
        
        # Add assistant prefix for the model to complete
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "huggingface_chat"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters."""
        return {
            "model_name": self.model_name,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }


class LLMFactory:
    """Factory for creating LLM instances."""
    
    @staticmethod
    def create_claude(
        api_key: Optional[str] = None,
        model: str = "claude-haiku-4-5-20251001",
        temperature: float = 0
    ) -> BaseChatModel:
        """
        Create Claude model instance.
        
        Args:
            api_key: Anthropic API key
            model: Claude model name
            temperature: Temperature for generation
            
        Returns:
            ChatAnthropic instance
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")
        
        logger.info(f"Creating Claude model: {model}")
        return ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            temperature=temperature
        )
    
    @staticmethod
    def create_huggingface(
        model_name: str = "Qwen/Qwen2.5-0.5B-Instruct",
        device: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        load_in_8bit: bool = False,
        load_in_4bit: bool = False
    ) -> BaseChatModel:
        """
        Create HuggingFace model instance.
        
        Args:
            model_name: HuggingFace model name (e.g., "Qwen/Qwen2.5-0.5B-Instruct")
            device: Device to use (cuda/cpu/mps). Auto-detected if None.
            max_new_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            load_in_8bit: Load model in 8-bit quantization
            load_in_4bit: Load model in 4-bit quantization
            
        Returns:
            HuggingFaceChatWrapper instance
        """
        # Lazy import HuggingFace dependencies (only when actually needed)
        logger.info("Importing HuggingFace dependencies...")
        try:
            import torch
            from transformers import (
                AutoTokenizer,
                AutoModelForCausalLM,
                pipeline,
            )
        except ImportError as e:
            raise ImportError(
                "HuggingFace dependencies not installed. Install with:\n"
                "  pip install torch transformers langchain-huggingface\n"
                f"Error: {e}"
            )
        
        logger.info(f"Loading HuggingFace model: {model_name}")
        
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        
        logger.info(f"Using device: {device}")
        
        # Load tokenizer
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Add pad token if it doesn't exist
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model with optional quantization
        logger.info("Loading model...")
        model_kwargs = {}
        
        if load_in_8bit:
            model_kwargs["load_in_8bit"] = True
            model_kwargs["device_map"] = "auto"
        elif load_in_4bit:
            model_kwargs["load_in_4bit"] = True
            model_kwargs["device_map"] = "auto"
        else:
            model_kwargs["torch_dtype"] = torch.float16 if device != "cpu" else torch.float32
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs
        )
        
        # Move to device if not using quantization (which uses device_map)
        if not load_in_8bit and not load_in_4bit:
            model = model.to(device)
        
        # Create pipeline
        logger.info("Creating text generation pipeline...")
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=device if device != "mps" else -1,  # pipeline doesn't support mps directly
        )
        
        # Wrap in chat interface
        logger.info("Model loaded successfully!")
        return HuggingFaceChatWrapper(
            pipeline=pipe,
            model_name=model_name,
            max_new_tokens=max_new_tokens,
            temperature=temperature
        )
    
    @staticmethod
    def create_model(
        model_type: ModelType = ModelType.CLAUDE,
        **kwargs
    ) -> BaseChatModel:
        """
        Create a model instance based on type.
        
        Args:
            model_type: Type of model to create
            **kwargs: Arguments passed to the specific model factory
            
        Returns:
            BaseChatModel instance
        """
        if model_type == ModelType.CLAUDE:
            return LLMFactory.create_claude(**kwargs)
        elif model_type == ModelType.HUGGINGFACE:
            return LLMFactory.create_huggingface(**kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")


# Convenience function
def create_llm(
    model_type: str = "claude",
    model_name: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """
    Convenience function to create an LLM.
    
    Args:
        model_type: "claude" or "huggingface"
        model_name: Specific model name (optional)
        **kwargs: Additional arguments for model creation
        
    Returns:
        BaseChatModel instance
        
    Examples:
        >>> # Create Claude model
        >>> llm = create_llm("claude", model="claude-haiku-4-5-20251001")
        
        >>> # Create HuggingFace model
        >>> llm = create_llm("huggingface", model_name="Qwen/Qwen2.5-0.5B-Instruct")
    """
    model_type_enum = ModelType(model_type.lower())
    
    if model_type_enum == ModelType.CLAUDE:
        if model_name:
            kwargs["model"] = model_name
        return LLMFactory.create_claude(**kwargs)
    else:
        if model_name:
            kwargs["model_name"] = model_name
        return LLMFactory.create_huggingface(**kwargs)


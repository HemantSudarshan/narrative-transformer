"""
Centralized LLM Client Factory
Provides unified API client with retry logic, JSON mode, and error handling.
"""

import json
import re
from typing import Optional, Dict, Any
from functools import wraps
import time

from openai import OpenAI
from anthropic import Anthropic

from config import DEFAULT_CONFIG

# Lazy import for Gemini to avoid deprecation warning when not using it
genai = None


def retry_with_backoff(max_retries: int = 3, base_delay: float = 2.0, max_delay: float = 10.0):
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        print(f"  ⚠️  API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        print(f"      Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                    else:
                        print(f"  ❌ API call failed after {max_retries + 1} attempts")
            raise last_exception
        return wrapper
    return decorator


class LLMClient:
    """
    Centralized LLM client with:
    - Unified API for OpenAI, Anthropic, and Gemini
    - Automatic retry with exponential backoff
    - JSON mode support for guaranteed parseable output
    - Consistent error handling
    """
    
    def __init__(self, model: Optional[str] = None, json_mode: bool = False):
        """
        Initialize LLM client.
        
        Args:
            model: Model name override (uses config default if None)
            json_mode: Enable JSON mode for guaranteed parseable output (OpenAI only)
        """
        self.config = DEFAULT_CONFIG
        self.model = model or self.config.default_model
        self.json_mode = json_mode
        
        # Initialize appropriate client
        if self.config.get_primary_api() == "gemini":
            # Lazy import Gemini SDK only when needed
            global genai
            import google.generativeai as genai
            genai.configure(api_key=self.config.gemini_api_key)
            self.client = genai.GenerativeModel(self.model)
            self.api_type = "gemini"
        elif self.config.get_primary_api() == "openai":
            client_kwargs = {"api_key": self.config.openai_api_key}
            if self.config.openai_base_url:
                client_kwargs["base_url"] = self.config.openai_base_url
                # OpenRouter requires these headers
                client_kwargs["default_headers"] = {
                    "HTTP-Referer": "https://github.com/narrative-transformer",
                    "X-Title": "Narrative Transformer"
                }
            self.client = OpenAI(**client_kwargs)
            self.api_type = "openai"
        elif self.config.get_primary_api() == "anthropic":
            self.client = Anthropic(api_key=self.config.anthropic_api_key)
            self.api_type = "anthropic"
        else:
            raise ValueError("No valid API key configured. Check your .env file.")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0, max_delay=10.0)
    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Make an LLM API call with retry logic.
        
        Args:
            prompt: User prompt/message
            system_prompt: System instruction (prepended for Gemini)
            temperature: Override config temperature
            max_tokens: Override config max_tokens
            
        Returns:
            LLM response text
        """
        temp = temperature if temperature is not None else self.config.temperature
        tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        if self.api_type == "gemini":
            return self._call_gemini(prompt, system_prompt, temp, tokens)
        elif self.api_type == "openai":
            return self._call_openai(prompt, system_prompt, temp, tokens)
        elif self.api_type == "anthropic":
            return self._call_anthropic(prompt, system_prompt, temp, tokens)
    
    def _call_gemini(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int
    ) -> str:
        """Call Gemini API."""
        # Gemini doesn't have separate system prompt, prepend to user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.client.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        return response.text
    
    def _call_openai(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int
    ) -> str:
        """Call OpenAI API with optional JSON mode."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Build request kwargs
        request_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Enable JSON mode if requested and supported
        if self.json_mode:
            request_kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**request_kwargs)
        return response.choices[0].message.content
    
    def _call_anthropic(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int
    ) -> str:
        """Call Anthropic API."""
        request_kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Anthropic supports system parameter
        if system_prompt:
            request_kwargs["system"] = system_prompt
        
        response = self.client.messages.create(**request_kwargs)
        return response.content[0].text
    
    @staticmethod
    def clean_json_response(response_text: str) -> str:
        """
        Clean LLM response to extract valid JSON.
        Removes markdown code blocks and extra whitespace.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Cleaned JSON string
        """
        json_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if json_text.startswith("```"):
            json_text = re.sub(r'^```json\s*', '', json_text)
            json_text = re.sub(r'^```\s*', '', json_text)
            json_text = re.sub(r'```\s*$', '', json_text)
        
        return json_text.strip()
    
    @staticmethod
    def parse_json_response(response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response as JSON with error handling.
        
        Args:
            response_text: Raw or cleaned LLM response
            
        Returns:
            Parsed JSON dict
            
        Raises:
            json.JSONDecodeError: If parsing fails
        """
        cleaned = LLMClient.clean_json_response(response_text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"   Response preview: {cleaned[:200]}...")
            raise


# Convenience function for quick usage
def get_llm_client(model: Optional[str] = None, json_mode: bool = False) -> LLMClient:
    """
    Get a configured LLM client instance.
    
    Args:
        model: Model name override
        json_mode: Enable JSON mode
        
    Returns:
        Configured LLMClient instance
    """
    return LLMClient(model=model, json_mode=json_mode)

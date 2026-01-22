"""
Base agent class with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import google.generativeai as genai

from config import settings
from utils.logger import logger


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, system_prompt: str, model_name: str = "gemini-2.5-flash"):
        """Initialize base agent."""
        self.system_prompt = system_prompt
        self.model_name = model_name
        
        # Configure Gemini API
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"Initialized {self.__class__.__name__} with model {model_name}")
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Process agent task (to be implemented by subclasses)."""
        pass
    
    def _create_prompt(self, user_input: str, context: Optional[str] = None) -> str:
        """Create a complete prompt with system prompt and user input."""
        prompt_parts = [self.system_prompt]
        
        if context:
            prompt_parts.append(f"\n\nCONTEXT:\n{context}")
        
        prompt_parts.append(f"\n\nUSER INPUT:\n{user_input}")
        
        return "\n".join(prompt_parts)
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API with the given prompt."""
        try:
            logger.debug(f"{self.__class__.__name__} calling Gemini API...")
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            logger.debug(f"{self.__class__.__name__} received response")
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
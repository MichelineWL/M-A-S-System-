"""
Custom Gemini LLM wrapper for PandasAI with configurable model.
"""
from pandasai.llm import GoogleGemini
from google import genai


class CustomGeminiLLM(GoogleGemini):
    """Custom Gemini LLM that properly supports model selection."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", **kwargs):
        """Initialize with specified model."""
        # Call parent init
        super().__init__(api_key=api_key, **kwargs)
        
        # Override the model
        self.model = model
        self._model = model
        self.model_name = model
        
        # Create new client with the API key
        self._client = genai.Client(api_key=api_key)
        
        # Configure generation parameters with adjusted settings for better responses
        self._generation_config = {
            "temperature": 0.9,  # Higher temperature for more creative/complete responses
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
            "frequency_penalty": 0.3,  # Reduce repetition
            "presence_penalty": 0.3,   # Encourage diverse responses
        }
    
    def call(self, instruction, suffix: str = "", context: str = None):
        """Override call to use our custom model with better prompting."""
        # Build comprehensive prompt for PandasAI
        prompt_parts = []
        
        # Convert instruction to string if it's a prompt object
        instruction_str = str(instruction) if not isinstance(instruction, str) else instruction
        
        # Add instruction
        prompt_parts.append(instruction_str)
        
        # Add context if provided
        if context:
            context_str = str(context) if not isinstance(context, str) else context
            prompt_parts.append(f"\n\nContext:\n{context_str}")
        
        # Add suffix if provided
        if suffix:
            suffix_str = str(suffix) if not isinstance(suffix, str) else suffix
            prompt_parts.append(f"\n\n{suffix_str}")
        
        # Add explicit instruction to return Python code
        prompt_parts.append("""

IMPORTANT: You MUST return valid Python code wrapped in ```python code blocks.
The code should define or update the analyze_data function.
Do not just describe what to do - write the actual executable Python code.""")
        
        prompt = "\n".join(prompt_parts)
        
        try:
            from google.genai import types
            
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self._generation_config["temperature"],
                    top_p=self._generation_config["top_p"],
                    top_k=self._generation_config["top_k"],
                    max_output_tokens=self._generation_config["max_output_tokens"],
                )
            )
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error with model {self.model}: {str(e)}")

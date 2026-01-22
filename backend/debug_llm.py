from pandasai.llm import GoogleGemini
import inspect

try:
    llm = GoogleGemini(api_key="test", model_name="gemini-2.5-flash")
    print(f"Model Name property: {getattr(llm, 'model_name', 'Not found')}")
    print(f"Internal _model_name: {getattr(llm, '_model_name', 'Not found')}")
    print(f"All attributes: {dir(llm)}")
    
    # Check constructor signature
    sig = inspect.signature(GoogleGemini.__init__)
    print(f"Constructor signature: {sig}")
    
except Exception as e:
    print(f"Error: {e}")

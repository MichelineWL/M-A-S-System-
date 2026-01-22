from pandasai.llm import GoogleGemini

try:
    llm_default = GoogleGemini(api_key="test")
    print(f"Default model value: {llm_default.model}")
    
    llm_custom = GoogleGemini(api_key="test", model="gemini-2.5-flash")
    print(f"Custom model value: {llm_custom.model}")
    
except Exception as e:
    print(f"Error: {e}")

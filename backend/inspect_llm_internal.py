from pandasai.llm import GoogleGemini
import os

# Check if we can find where it's defined
print(f"File: {GoogleGemini.__module__}")

llm = GoogleGemini(api_key="test", model="gemini-2.5-flash")
print(f"Model attribute: {llm.model}")

# Let's try to see if it has a 'google_gemini' attribute which is the underlying genai object
if hasattr(llm, 'google_gemini'):
    print(f"Underlying model: {llm.google_gemini.model_name}")

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv('.env')
api_key = os.getenv('GEMINI_API_KEY')

print(f"API Key: {api_key[:20]}...")
print(f"SDK Version: {genai.__version__}\n")

# Configure API
genai.configure(api_key=api_key)

print("=" * 60)
print("AVAILABLE MODELS:")
print("=" * 60)

try:
    models = genai.list_models()
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display: {model.display_name}")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")
            print()
except Exception as e:
    print(f"Error listing models: {e}")

print("\n" + "=" * 60)
print("TESTING MODEL CALLS:")
print("=" * 60)

test_models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
]

for model_name in test_models:
    print(f"\nTesting: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say OK")
        print(f"✅ SUCCESS - Response: {response.text.strip()}")
    except Exception as e:
        print(f"❌ FAILED - {str(e)[:100]}")

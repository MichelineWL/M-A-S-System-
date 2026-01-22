"""Test PandasAI GoogleGemini model parameter."""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')
api_key = os.getenv('GEMINI_API_KEY')

print("Testing PandasAI GoogleGemini initialization...")
print("=" * 60)

try:
    from pandasai.llm import GoogleGemini
    import inspect
    
    # Check the signature
    sig = inspect.signature(GoogleGemini.__init__)
    print(f"GoogleGemini.__init__ signature:\n{sig}\n")
    
    # Check parameters
    print("Parameters:")
    for param_name, param in sig.parameters.items():
        if param_name != 'self':
            print(f"  - {param_name}: {param.annotation} = {param.default}")
    
    print("\n" + "=" * 60)
    print("Testing different initialization methods:")
    print("=" * 60)
    
    # Test 1: Default (this might use gemini-pro)
    print("\n1. Default initialization:")
    try:
        llm1 = GoogleGemini(api_key=api_key)
        print(f"✅ Success")
        if hasattr(llm1, 'model'):
            print(f"   Model: {llm1.model}")
        if hasattr(llm1, 'model_name'):
            print(f"   Model name: {llm1.model_name}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: With model parameter
    print("\n2. With model='gemini-2.0-flash':")
    try:
        llm2 = GoogleGemini(api_key=api_key, model="gemini-2.0-flash")
        print(f"✅ Success")
        if hasattr(llm2, 'model'):
            print(f"   Model: {llm2.model}")
        if hasattr(llm2, 'model_name'):
            print(f"   Model name: {llm2.model_name}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: Check source code
    print("\n3. GoogleGemini source file location:")
    import pandasai.llm
    print(f"   {pandasai.llm.__file__}")
    
except ImportError as e:
    print(f"❌ Cannot import PandasAI: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

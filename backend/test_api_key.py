import google.generativeai as genai
from config import Config

def test_api_key():
    try:
        print("Testing API key...")
        print(f"API key found (length: {len(Config.GEMINI_API_KEY)})")
        
        # Configure API
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # List models
        print("\nListing available models:")
        models = genai.list_models()
        for model in models:
            print(f"- {model.name}")
        
        # Test simple generation
        print("\nTesting simple generation:")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        print(f"Response: {response.text}")
        
        print("\nAPI key test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing API key: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key()
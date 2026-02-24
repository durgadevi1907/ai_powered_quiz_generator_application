import google.generativeai as genai
from config import Config

def test_gemini_api():
    try:
        # Configure the API
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            return "Error: GEMINI_API_KEY not found"
            
        genai.configure(api_key=api_key)
        
        # List available models
        print("Available models:")
        for m in genai.list_models():
            print(f"- {m.name}")
        
        # Try to create a model instance
        model = genai.GenerativeModel('gemini-1.0-pro')
        
        # Try a simple generation
        response = model.generate_content("Hello, what can you do?")
        print("\nTest response:", response.text)
        
        return "Success: API is working correctly"
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(test_gemini_api())
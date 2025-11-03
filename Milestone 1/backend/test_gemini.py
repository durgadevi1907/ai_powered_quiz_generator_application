from config import Config
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini_api():
    try:
        # Configure API
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Checking environment variables:")
            print("GOOGLE_API_KEY:", os.getenv('GOOGLE_API_KEY'))
            print("GEMINI_API_KEY:", os.getenv('GEMINI_API_KEY'))
            return "Error: No API key found"
            
        genai.configure(api_key=api_key)
        
        print("\nAvailable models:")
        for m in genai.list_models():
            print(f"- {m.name}")
            
        # Initialize the model
        model = genai.GenerativeModel('models/gemini-pro-latest')

        # Test prompt
        prompt = """Create 1 multiple choice question about Python programming.Required format:
{
    "questions": [
        {
            "question": "What is the correct way to define a function in Python?",
            "options": ["function name():", "def name():", "define name():", "func name():"],
            "answer": "def name():"
        }
    ]
}

Requirements:
1. Response must be a single valid JSON object
2. Must have a 'questions' array
3. Question must have exactly 4 options
4. Answer must match one of the options exactly

Important: Return ONLY the JSON object, no additional text."""

        # Generate response
        print("\nSending request to Gemini API...")
        response = model.generate_content(prompt)
        
        print("\nRaw response:")
        print(response.text)
        
        # Clean response
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        print("\nCleaned response:")
        print(text)
        
        # Parse JSON
        data = json.loads(text)
        print("\nParsed JSON:")
        print(json.dumps(data, indent=2))
        
        return "Success"
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(test_gemini_api())
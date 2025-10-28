from config import Config
import google.generativeai as genai
import json

def test_gemini_api():
    try:
        # Configure API
        api_key = Config.GEMINI_API_KEY
        if not api_key:
            return "Error: GEMINI_API_KEY not found"
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')
        
        # Test prompt
        prompt = """Create 1 multiple choice question about Python programming.

Required format:
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
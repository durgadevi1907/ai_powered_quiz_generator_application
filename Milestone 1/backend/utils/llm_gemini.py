import requests
import json
from config import Config

class GeminiLLM:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.api_url = Config.GEMINI_API_URL
    
    def generate_questions(self, topic, number_questions):
        """
        Generate quiz questions using Gemini API
        """
        prompt = f"""
        Generate exactly {number_questions} multiple choice questions about {topic}.
        For each question, provide:
        1. The question text
        2. Four options (A, B, C, D)
        3. The correct answer
        
        Format the response as a JSON object with the following structure:
        {{
            "questions": [
                {{
                    "question": "question text here",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Correct option text"
                }}
            ]
        }}
        
        Make sure the questions are diverse and cover different aspects of {topic}.
        Ensure each question has exactly 4 options.
        """
        
        payload = json.dumps({
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            }
        })
        
        headers = {
            'X-goog-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, data=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the text from Gemini response
            if 'candidates' in result and len(result['candidates']) > 0:
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                
                # Clean the response (remove markdown code blocks if present)
                text_response = text_response.replace('```json', '').replace('```', '').strip()
                
                # Parse the JSON response
                questions_data = json.loads(text_response)
                return questions_data
            else:
                raise Exception("No response from Gemini API")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse API response: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")

# Singleton instance
gemini_llm = GeminiLLM()
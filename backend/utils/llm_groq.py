from typing import List
from pydantic import BaseModel
from openai import OpenAI
import json
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =========================
# ✅ Pydantic Models
# =========================
class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answers: List[str]
    explanation: str
    sub_topic: str

class QuizQuestionSet(BaseModel):
    questions: List[QuizQuestion]

# =========================
# ✅ AI Service (Groq)
# =========================
class GroqAIService:
    """AI Service using Groq API for generating quiz questions"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY missing")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def generate_quiz_questions(self, domain, sub_domain, number_of_questions, level, previous_questions=None):
        """Generate quiz questions using Groq API"""
        number_of_questions = min(number_of_questions, 5)

        # Build previous questions text
        prev_q_text = ""
        if previous_questions:
            prev_q_text = f"""
AVOID these already used questions:
{chr(10).join(f'- {q}' for q in previous_questions)}
"""

        # Difficulty-specific instructions
        difficulty_instructions = {
            "easy": "Use simple language. Questions should be straightforward and suitable for beginners.",
            "intermediate": "Use moderate complexity. Questions should require some knowledge of the topic.",
            "hard": "Use advanced concepts. Questions should be challenging and require deep understanding."
        }
        difficulty_hint = difficulty_instructions.get(level, difficulty_instructions["intermediate"])

        prompt = f"""
Generate {number_of_questions} {level} difficulty MCQs on "{sub_domain}" from "{domain}".
{prev_q_text}
Difficulty guidance: {difficulty_hint}

STRICT:
- Return ONLY valid JSON
- No markdown
- No extra text
- Do NOT repeat any of the above questions
FORMAT:
{{
  "questions": [
    {{
      "id": 1,
      "question": "text",
      "options": ["A","B","C","D"],
      "correct_answers": ["A"],
      "explanation": "text",
      "sub_topic": "text"
    }}
  ]
}}
"""
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
            print("✅ RAW RESPONSE:\n", content)

            # =========================
            # 🔥 CLEAN JSON
            # =========================
            content = content.strip()
            content = content.replace("```json", "").replace("```", "")
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]

            # remove trailing commas
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r",\s*]", "]", json_str)

            parsed = json.loads(json_str)
            validated = QuizQuestionSet(**parsed)
            result = [q.model_dump() for q in validated.questions]
            print("🎯 PARSED QUESTIONS:\n", result)
            return result

        except Exception as e:
            print("❌ ERROR:", str(e))
            return {
                "error": str(e),
                "questions": []
            }

# For backwards compatibility
class GeminiClient(GroqAIService):
    """Deprecated: Use GroqAIService instead"""
    
    def __init__(self):
        super().__init__()
    
    def generate_questions(self, topic: str, number_questions: int, previous_questions=None, difficulty="intermediate"):
        """Backwards compatibility wrapper"""
        try:
            result = self.generate_quiz_questions(
                domain=topic,
                sub_domain=topic,
                number_of_questions=number_questions,
                level=difficulty,
                previous_questions=previous_questions
            )
            if isinstance(result, dict) and "error" in result:
                return result
            return {"questions": result}
        except Exception as e:
            print("❌ ERROR:", str(e))
            return {"error": str(e), "questions": []}


class AIService(GroqAIService):
    """Alias for GroqAIService - main service class"""
    pass


# =========================
# 🔧 Module-level Instances
# =========================
_groq_service = None
_gemini_llm = None

def get_groq_service():
    """Get or create a GroqAIService instance"""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqAIService()
    return _groq_service

def get_gemini_llm():
    """Get or create a GeminiClient instance (backwards compatibility)"""
    global _gemini_llm
    if _gemini_llm is None:
        _gemini_llm = GeminiClient()
    return _gemini_llm

# Module-level instance for backwards compatibility
groq_llm = None
gemini_llm = None

try:
    groq_llm = get_groq_service()
    gemini_llm = get_gemini_llm()
except Exception as e:
    print(f"⚠️ Warning: Could not initialize Groq service: {str(e)}")

def generate_questions(topic: str, number_of_questions: int, previous_questions=None, difficulty="intermediate"):
    """Generate quiz questions using Groq - main function"""
    try:
        service = get_groq_service()
        return service.generate_quiz_questions(
            domain=topic,
            sub_domain=topic,
            number_of_questions=number_of_questions,
            level=difficulty,
            previous_questions=previous_questions
        )
    except Exception as e:
        print(f"❌ Error generating questions: {str(e)}")
        return {"error": str(e), "questions": []}
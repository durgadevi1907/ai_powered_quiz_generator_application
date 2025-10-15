import json
import re
from typing import List
from pydantic import BaseModel, Field, validator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from config import Config


class QuizQuestion(BaseModel):
    """Pydantic model for a single quiz question"""
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of 4 answer options")
    answer: str = Field(..., description="The correct answer option")
    
    @validator('options')
    def validate_options(cls, v):
        if len(v) != 4:
            raise ValueError('Each question must have exactly 4 options')
        return v
    
    @validator('answer')
    def validate_answer(cls, v, values):
        if 'options' in values and v not in values['options']:
            raise ValueError('Answer must be one of the provided options')
        return v


class QuizData(BaseModel):
    """Pydantic model for the complete quiz data"""
    questions: List[QuizQuestion] = Field(..., description="List of quiz questions")
    
    @validator('questions')
    def validate_questions_not_empty(cls, v):
        if not v:
            raise ValueError('Quiz must have at least one question')
        return v


class GeminiLLM:
    """Gemini LLM wrapper using LangChain and Pydantic for structured output"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", temperature: float = 0.7):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = model_name
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature,
            max_output_tokens=2048
        )
    
    def generate_questions(self, topic: str, number_questions: int) -> List[dict]:
        """Generate quiz questions using Gemini API with structured output"""
        try:
            prompt = f"""Generate {number_questions} multiple choice questions about the topic: "{topic}".

Requirements:
- Each question should have exactly 4 options
- Only one option should be correct
- Questions should be educational and appropriate
- The answer field should contain the exact text of the correct option

Generate exactly {number_questions} questions."""

            # Invoke the structured LLM
            result: QuizData = self.llm.with_structured_output(QuizData).invoke(prompt)
            
            # Convert Pydantic models to dictionaries
            return [question.model_dump() for question in result.questions]
            
        except Exception as e:
            try:
                return self._fallback_parsing(topic, number_questions)
            except Exception as fallback_error:
                raise Exception(f"Error generating questions: {str(e)}. Fallback also failed: {str(fallback_error)}")
    
    def _fallback_parsing(self, topic: str, number_questions: int) -> List[dict]:
        """Fallback method using raw text parsing if structured output fails"""
        prompt = f"""Generate exactly {number_questions} multiple choice questions about {topic}.

Format the response as a JSON object:
{{
    "questions": [
        {{
            "question": "question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Correct option text"
        }}
    ]
}}

Make sure each question has exactly 4 options and covers different aspects of {topic}."""
        
        message = HumanMessage(content=prompt)
        response = self.llm.invoke([message])
        
        text_response = response.content.replace('```json', '').replace('```', '').strip()
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            return [question for question in data["questions"]]
        else:
            raise Exception("Could not extract JSON from response")


# Singleton instance
gemini_llm = GeminiLLM()
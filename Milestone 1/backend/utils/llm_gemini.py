import os
from typing import List, Dict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

class Question(BaseModel):
    """Pydantic model for a single quiz question"""
    question: str = Field(description="The quiz question text")
    options: List[str] = Field(description="List of exactly 4 answer options")
    answer: str = Field(description="The correct answer from the options")

    def clean(self) -> None:
        """Clean up text fields by removing extra whitespace"""
        self.question = " ".join(self.question.split())
        self.answer = " ".join(self.answer.split())
        self.options = [" ".join(opt.split()) for opt in self.options]

    def is_valid(self) -> bool:
        """Validate that answer exists in options and there are exactly 4 options"""
        return (
            len(self.options) == 4 and
            all(isinstance(opt, str) and opt.strip() for opt in self.options) and
            self.answer in self.options
        )

class QuizQuestions(BaseModel):
    """Pydantic model for a collection of quiz questions"""
    questions: List[Question] = Field(description="List of generated quiz questions")

class GeminiClient:
    """Client for generating quiz questions using Gemini LLM with structured output"""
    
    def __init__(self):
        """Initialize the Gemini client with structured output support"""
        # Get and validate API key
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Neither GOOGLE_API_KEY nor GEMINI_API_KEY found in environment variables")
        if len(self.api_key) < 10:
            raise ValueError("API key appears to be invalid")

        try:
            # Initialize ChatGoogleGenerativeAI with structured output
            self.llm = ChatGoogleGenerativeAI(
                model="models/gemini-pro-latest",
                google_api_key=self.api_key,
                temperature=0.7,
                convert_system_message_to_human=True,
                max_output_tokens=2048
            )

            # Create structured output LLM
            self.structured_llm = self.llm.with_structured_output(QuizQuestions)
            
        except Exception as e:
            print(f"Error initializing Gemini model: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini model: {str(e)}")

    def generate_questions(self, topic: str, number_questions: int) -> Dict[str, List[Dict]]:
        """Generate multiple choice questions using structured output"""
        try:
            prompt = f"""
            Generate {number_questions} multiple choice questions about the topic: "{topic}".
            
            Requirements:
            1. Each question MUST have exactly 4 answer options
            2. Only one option should be correct
            3. Questions should be educational and fact-based
            4. The answer field must contain the exact text of the correct option
            5. All questions should be appropriate and accurate
            
            Example format:
            {{
                "questions": [
                    {{
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],
                        "answer": "Paris"
                    }}
                ]
            }}

            Generate exactly {number_questions} questions.
            """

            # Generate questions using structured output
            result: QuizQuestions = self.structured_llm.invoke(prompt)
            
            # Validate and clean questions
            valid_questions = []
            for question in result.questions:
                try:
                    # Clean the text
                    question.clean()
                    # Validate the question
                    if question.is_valid():
                        valid_questions.append(question)
                except Exception as e:
                    print(f"Error processing question: {str(e)}")
                    continue
            
            if not valid_questions:
                raise ValueError("No valid questions generated")
            
            # Convert to dictionary format and return
            return {
                "questions": [
                    question.model_dump() 
                    for question in valid_questions[:number_questions]
                ]
            }
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            raise ValueError(f"Failed to generate questions: {str(e)}")

# Singleton instance and initialization function
_gemini_instance = None

def get_gemini_client():
    """Get or create the GeminiClient instance"""
    global _gemini_instance
    if _gemini_instance is None:
        try:
            _gemini_instance = GeminiClient()
        except Exception as e:
            print(f"Error initializing Gemini client: {str(e)}")
            raise
    return _gemini_instance

def generate_questions(topic: str, number_questions: int) -> Dict[str, List[Dict]]:
    """Generate quiz questions using the GeminiClient instance"""
    try:
        client = get_gemini_client()
        return client.generate_questions(topic, number_questions)
    except Exception as e:
        print(f"Error in generate_questions: {str(e)}")
        raise ValueError(f"Failed to generate questions: {str(e)}")
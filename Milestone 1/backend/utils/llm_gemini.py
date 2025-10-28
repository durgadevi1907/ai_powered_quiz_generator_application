import os
import time
from typing import List, Dict, Optional
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

    def clean_text(self) -> None:
        """Clean up text fields by normalizing whitespace"""
        self.question = " ".join(line.strip() for line in self.question.splitlines())
        self.answer = " ".join(line.strip() for line in self.answer.splitlines())
        self.options = [" ".join(line.strip() for line in opt.splitlines()) for opt in self.options]

    def validate_answer(self) -> bool:
        """Validate that answer exists in options"""
        return (
            len(self.options) == 4 and
            all(isinstance(opt, str) and opt.strip() for opt in self.options) and
            self.answer in self.options
        )

class QuizQuestions(BaseModel):
    """Pydantic model for a collection of quiz questions"""
    questions: List[Question] = Field(description="List of generated quiz questions")

class GeminiClient:
    """Client for generating quiz questions using Google's Gemini AI"""
    
    def __init__(self):
        """Initialize the Gemini client with multiple model support and rate limiting"""
        # Get and validate API key
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        if len(self.api_key) < 10:
            raise ValueError("GEMINI_API_KEY appears to be invalid")

        print(f"API Key found (length: {len(self.api_key)})")

        # Model configuration
        self.model_configs = [
            {"name": "gemini-2.5-pro", "temperature": 0.7},
            {"name": "gemini-2.0-pro-exp", "temperature": 0.7},
            {"name": "gemini-2.5-flash", "temperature": 0.7},
            {"name": "gemini-flash-latest", "temperature": 0.7}
        ]

        # Initialize models
        self.models: Dict[str, ChatGoogleGenerativeAI] = {}
        self.current_model: Optional[str] = None
        
        print("\nInitializing Gemini models...")
        for config in self.model_configs:
            try:
                model = ChatGoogleGenerativeAI(
                    model=config["name"],
                    google_api_key=self.api_key,
                    temperature=config["temperature"]
                )
                
                # Create structured output wrapper
                structured_model = model.with_structured_output(QuizQuestions)
                
                # Test the model
                test_prompt = "Generate 1 simple test question about math."
                try:
                    result = structured_model.invoke(test_prompt)
                    if result and result.questions:
                        print(f"Successfully initialized {config['name']}")
                        self.models[config["name"]] = structured_model
                        if not self.current_model:
                            self.current_model = config["name"]
                except Exception as test_error:
                    print(f"Failed to test {config['name']}: {str(test_error)}")
                    continue
                    
            except Exception as e:
                print(f"Failed to initialize {config['name']}: {str(e)}")
                continue

        if not self.models:
            raise ValueError("Failed to initialize any models")

        # Initialize rate limit tracking
        self.request_times: Dict[str, List[float]] = {
            model: [] for model in self.models
        }
        
        n_models = len(self.models)
        print(f"\nInitialization complete:")
        print(f"- {n_models} models available")
        print(f"- Using {self.current_model} as primary model")
        print(f"- {n_models-1} fallback models ready")

    def _check_rate_limit(self, model_name: str) -> bool:
        """Check if we're within rate limits for a model"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.request_times[model_name] = [
            t for t in self.request_times[model_name] 
            if t > minute_ago
        ]
        
        # Check if we're within limits
        return len(self.request_times[model_name]) < 2  # 2 requests per minute
        
    def _update_rate_limit(self, model_name: str):
        """Record a request for rate limiting"""
        self.request_times[model_name].append(time.time())

    def generate_questions(self, topic: str, number_questions: int) -> Dict[str, List[Dict]]:
        """Generate multiple choice questions about a topic.

        Args:
            topic (str): Topic to generate questions about
            number_questions (int): Number of questions to generate

        Returns:
            Dict[str, List[Dict]]: Dictionary containing:
                {
                    'questions': [
                        {
                            'question': str,
                            'options': List[str],
                            'answer': str
                        },
                        ...
                    ]
                }

        Raises:
            ValueError: If unable to generate valid questions
        """
        try:
            prompt = f"""
            Generate {number_questions} multiple choice questions about the topic: "{topic}".
            
            Requirements:
            1. Each question should have exactly 4 options
            2. Only one option should be correct
            3. Questions should be educational and appropriate
            4. The answer field should contain the exact text of the correct option
            5. Questions should be challenging but fair
            6. No explanations needed, just questions
            
            Generate exactly {number_questions} questions.
            """

            print(f"Generating {number_questions} questions about {topic}...")
            
            max_retries = 3
            retry_count = 0
            last_error = None
            
            # Try models in sequence
            for model_name, model in self.models.items():
                for attempt in range(max_retries):
                    try:
                        # Check rate limits
                        if not self._check_rate_limit(model_name):
                            wait_time = 60  # Wait for rate limit reset
                            print(f"Rate limit reached for {model_name}, waiting {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                            
                        print(f"Attempt {attempt + 1}/3 with model {model_name}")
                        
                        # Make request
                        result: QuizQuestions = model.invoke(prompt)
                        self._update_rate_limit(model_name)
                        
                        # Validate and clean questions
                        valid_questions = []
                        for q in result.questions:
                            try:
                                # Clean text
                                q.clean_text()
                                
                                # Validate
                                if q.validate_answer():
                                    valid_questions.append(q)
                                else:
                                    print(f"Invalid question (answer not in options): {q.question}")
                                    
                            except Exception as e:
                                print(f"Error validating question: {str(e)}")
                                continue
                                
                        if valid_questions:
                            print(f"\nGenerated {len(valid_questions)} valid questions using {model_name}")
                            return {"questions": [q.model_dump() for q in valid_questions[:number_questions]]}
                            
                    except Exception as e:
                        last_error = e
                        error_msg = str(e)
                        print(f"Error with {model_name}: {error_msg}")
                        
                        if "429" in error_msg or "quota" in error_msg.lower():
                            # Rate limit hit - wait and retry
                            wait_time = min(60 * (2 ** attempt), 300)  # Max 5 min wait
                            print(f"Rate limited, waiting {wait_time}s...")
                            time.sleep(wait_time)
                        elif "404" in error_msg:
                            print(f"Model {model_name} not found, trying next...")
                            break  # Try next model
                        else:
                            # Other error - exponential backoff
                            wait_time = min(2 ** attempt * 10, 120)
                            print(f"Error occurred, waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                            
            # If we get here, all models failed
            error_msg = str(last_error) if last_error else "Failed to generate valid questions"
            raise ValueError(f"Question generation failed: {error_msg}")
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            raise ValueError(f"Failed to generate questions: {str(e)}")

# Singleton instance
gemini_llm = GeminiClient()
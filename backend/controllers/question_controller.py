from utils.llm_groq import gemini_llm
from flask_restx import Resource
from models.question_models import question_request_model, questions_response_model
from flask import request
from flask_restx import marshal

class QuestionGenerator(Resource):
    def post(self):
        """
        Generate quiz questions based on topic
        """
        try:
            # Get request data
            data = request.get_json()
            
            # Validate required fields
            if not data or 'topic' not in data or 'number_questions' not in data:
                return {
                    'error': 'Missing required fields: topic and number_questions are required'
                }, 400
            
            topic = data['topic']
            number_questions = data['number_questions']
            
            # Validate number_questions
            if not isinstance(number_questions, int) or number_questions < 1 or number_questions > 20:
                return {
                    'error': 'number_questions must be an integer between 1 and 20'
                }, 400
            
            print(f"\nGenerating {number_questions} questions about: {topic}")
            
            try:
                # Generate questions using Gemini
                questions = gemini_llm.generate_questions(topic, number_questions)
                
                # Ensure we have a list of questions
                if isinstance(questions, dict) and 'questions' in questions:
                    questions = questions['questions']
                
                if not isinstance(questions, list):
                    print(f"Error: Invalid response type: {type(questions)}")
                    return {
                        'error': 'Invalid response format from AI service',
                        'detail': f'Expected list or dict with questions, got {type(questions)}'
                    }, 500
                
                if not questions:
                    print("Error: No questions were generated")
                    return {
                        'error': 'No questions were generated',
                        'detail': 'The AI service returned an empty list'
                    }, 500
                
                # Validate each question
                valid_questions = []
                for idx, q in enumerate(questions):
                    # Basic type check
                    if not isinstance(q, dict):
                        print(f"Question {idx} is not a dictionary: {type(q)}")
                        continue
                    
                    # Check required fields
                    if not all(k in q for k in ['question', 'options', 'answer']):
                        missing = [k for k in ['question', 'options', 'answer'] if k not in q]
                        print(f"Question {idx} missing fields: {missing}")
                        continue
                    
                    # Validate options
                    if not isinstance(q['options'], list):
                        print(f"Question {idx} options is not a list: {type(q['options'])}")
                        continue
                    
                    if len(q['options']) != 4:
                        print(f"Question {idx} has {len(q['options'])} options, expected 4")
                        continue
                    
                    # Validate answer
                    if q['answer'] not in q['options']:
                        print(f"Question {idx} answer not in options")
                        continue
                    
                    valid_questions.append(q)
                
                if not valid_questions:
                    return {
                        'error': 'No valid questions generated',
                        'detail': 'All generated questions failed validation'
                    }, 500
                
                print(f"Successfully validated {len(valid_questions)} questions")
                
                # Return the requested number of questions
                response = {
                    'questions': valid_questions[:number_questions]
                }
                
                return marshal(response, questions_response_model), 200
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error generating questions: {error_msg}")
                
                if "429" in error_msg:
                    return {
                        'error': 'API rate limit exceeded',
                        'detail': 'Please try again in a minute'
                    }, 429
                elif "quota" in error_msg.lower():
                    return {
                        'error': 'API quota exceeded',
                        'detail': 'Please try again later'
                    }, 429
                else:
                    return {
                        'error': 'Failed to generate questions',
                        'detail': error_msg
                    }, 500
                    
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {
                'error': 'Internal server error',
                'detail': str(e)
            }, 500
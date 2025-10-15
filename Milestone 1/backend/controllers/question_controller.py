from utils.llm_gemini import gemini_llm
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
            
            # Generate questions using Gemini
            questions_list = gemini_llm.generate_questions(topic, number_questions)
            
            # Validate the response structure
            if not isinstance(questions_list, list):
                return {
                    'error': 'Invalid response format from AI service'
                }, 500
            
            # Ensure we have the requested number of questions
            actual_questions = questions_list[:number_questions]
            
            response = {
                'questions': actual_questions
            }
            
            return marshal(response, questions_response_model), 200
            
        except Exception as e:
            return {
                'error': f'Failed to generate questions: {str(e)}'
            }, 500
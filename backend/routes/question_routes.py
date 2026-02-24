from flask_restx import Namespace, fields, Resource
from flask import request
import json
from utils.llm_groq import generate_questions

# Create namespace
questions_ns = Namespace('questions', description='Question generation operations')

# Define models
question_request_model = questions_ns.model('QuestionRequest', {
    'topic': fields.String(required=True, description='Topic for question generation'),
    'number_questions': fields.Integer(required=True, description='Number of questions to generate', min=1, max=20)
})

question_model = questions_ns.model('Question', {
    'question': fields.String(description='The question text'),
    'options': fields.List(fields.String, description='List of options'),
    'answer': fields.String(description='Correct answer')
})

questions_response_model = questions_ns.model('QuestionsResponse', {
    'questions': fields.List(fields.Nested(question_model), description='List of generated questions')
})

@questions_ns.route('/generate')
class GenerateQuestions(Resource):
    @questions_ns.expect(question_request_model)
    @questions_ns.response(200, 'Success', questions_response_model)
    @questions_ns.response(400, 'Bad Request')
    @questions_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Generate quiz questions based on a topic
        """
        try:
            # Get request data
            data = request.get_json()
            
            print(f"Received request: {data}")  # Debug log
            
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
            
            print(f"Generating {number_questions} questions about: {topic}")  # Debug log
            
            # Generate questions using Gemini
            questions_data = generate_questions(topic, number_questions)
            
            # Validate the response structure
            if isinstance(questions_data, list):
                questions_data = {'questions': questions_data}

            # Validate the response structure
            if 'questions' not in questions_data:
                return {
                    'error': 'Invalid response format from AI service'
                }, 500
            
            # Ensure we have the requested number of questions
            actual_questions = questions_data['questions'][:number_questions]
            
            response = {
                'questions': actual_questions
            }
            
            print(f"Generated {len(actual_questions)} questions successfully")  # Debug log
            return response, 200
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")  # Debug log
            return {
                'error': f'Failed to generate questions: {str(e)}'
            }, 500
@questions_ns.route('/test')
class TestRoute(Resource):
    def get(self):
        """Test route to verify the namespace is working"""
        return {
            "message": "Questions namespace is working!",
            "endpoints": {
                "POST /generate-questions": "Generate quiz questions"
            }
        }
from flask_restx import fields
from flask_restx import Model

question_request_model = Model('QuestionRequest', {
    'topic': fields.String(required=True, description='Topic for question generation'),
    'number_questions': fields.Integer(required=True, description='Number of questions to generate', min=1, max=20)
})

option_model = Model('Option', {
    'options': fields.List(fields.String, description='List of options'),
    'answer': fields.String(description='Correct answer')
})

question_model = Model('Question', {
    'question': fields.String(description='The question text'),
    'options': fields.List(fields.String, description='List of options'),
    'answer': fields.String(description='Correct answer')
})

questions_response_model = Model('QuestionsResponse', {
    'questions': fields.List(fields.Nested(question_model), description='List of generated questions')
})
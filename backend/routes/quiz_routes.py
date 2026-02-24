from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from database.db import get_db_connection
from datetime import datetime, timedelta
from controllers.auth_controller import auth_required
from utils.llm_groq import generate_questions

quiz_ns = Namespace('quiz', description='Quiz operations')

# Models
quiz_attempt_model = quiz_ns.model('QuizAttempt', {
    'quiz_id': fields.Integer(description='Quiz ID for incomplete quiz'),
    'topic': fields.String(required=True, description='Quiz topic'),
    'score': fields.Integer(required=True, description='Score obtained'),
    'total_questions': fields.Integer(required=True, description='Total number of questions'),
    'answers': fields.String(description='JSON string of user answers')
})

quiz_create_model = quiz_ns.model('QuizCreate', {
    'topic': fields.String(required=True, description='Quiz topic'),
    'total_questions': fields.Integer(required=True, description='Total number of questions')
})

@quiz_ns.route('/create')
class CreateQuiz(Resource):
    @auth_required
    @quiz_ns.expect(quiz_create_model)
    def post(self):
        try:
            token = request.headers.get('Authorization')
            data = request.get_json()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user_id from token
            cursor.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
            user_data = cursor.fetchone()
            if not user_data:
                return {'message': 'Invalid token'}, 401
                
            user_id = user_data['user_id']
            
            # Insert quiz attempt as incomplete (store questions if provided)
            questions_json = None
            if 'questions' in data:
                # Expecting data['questions'] to be a JSON-serializable object (list/dict)
                try:
                    import json as _json
                    questions_json = _json.dumps(data['questions'])
                except Exception:
                    questions_json = None

            cursor.execute('''
                INSERT INTO quiz_attempts (
                    user_id, topic, total_questions,
                    questions, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data['topic'],
                data['total_questions'],
                questions_json,
                'incomplete',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            quiz_id = cursor.lastrowid
            conn.commit()
            
            return {'message': 'Quiz created successfully', 'quiz_id': quiz_id}, 200
            
        except Exception as e:
            print(f"Error creating quiz: {str(e)}")
            return {'error': 'Failed to create quiz'}, 500
        finally:
            conn.close()

@quiz_ns.route('/<int:quiz_id>')
class GetQuiz(Resource):
    @auth_required
    def get(self, quiz_id):
        try:
            token = request.headers.get('Authorization')
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user_id from token
            cursor.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
            user_data = cursor.fetchone()
            if not user_data:
                return {'message': 'Invalid token'}, 401
                
            user_id = user_data['user_id']
            
            # Get quiz attempt
            cursor.execute('''
                SELECT * FROM quiz_attempts 
                WHERE id = ? AND user_id = ? AND status = 'incomplete'
            ''', (quiz_id, user_id))
            
            quiz = cursor.fetchone()
            if not quiz:
                return {'message': 'Quiz not found or already completed'}, 404

            # If questions were stored at creation time, return them; otherwise generate
            stored_questions = quiz['questions'] if 'questions' in quiz.keys() else None
            if stored_questions:
                try:
                    import json as _json
                    questions_obj = _json.loads(stored_questions)
                except Exception:
                    questions_obj = None
            else:
                questions_obj = None

            if not questions_obj:
                # Fallback: generate questions dynamically (may fail if LLM unavailable)
                try:
                    questions_obj = generate_questions(quiz['topic'], quiz['total_questions'])
                except Exception as e:
                    print(f"Error generating questions for quiz {quiz_id}: {e}")
                    return {'error': 'Failed to fetch quiz questions'}, 500

            return {
                'id': quiz['id'],
                'topic': quiz['topic'],
                'total_questions': quiz['total_questions'],
                'questions': questions_obj.get('questions') if isinstance(questions_obj, dict) else questions_obj
            }
            
        except Exception as e:
            print(f"Error fetching quiz: {str(e)}")
            return {'error': 'Failed to fetch quiz'}, 500
        finally:
            conn.close()

@quiz_ns.route('/submit')
class SubmitQuiz(Resource):
    @auth_required
    @quiz_ns.expect(quiz_attempt_model)
    def post(self):
        try:
            token = request.headers.get('Authorization')
            data = request.get_json()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user_id from token
            cursor.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
            user_data = cursor.fetchone()
            if not user_data:
                return {'message': 'Invalid token'}, 401
                
            user_id = user_data['user_id']
            
            quiz_id = data.get('quiz_id')
            
            if not quiz_id:
                return {'message': 'Quiz ID is required'}, 400
                
            # Update existing quiz status
            cursor.execute('''
                UPDATE quiz_attempts 
                SET status = 'completed', 
                    score = ?, 
                    answers = ?,
                    completed_at = ?
                WHERE id = ? AND user_id = ? AND status = 'incomplete'
            ''', (
                data['score'],
                data.get('answers'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                quiz_id,
                user_id
            ))
            
            conn.commit()
            
            return {'message': 'Quiz submitted successfully'}, 200
            
        except Exception as e:
            print(f"Error submitting quiz: {str(e)}")
            return {'error': 'Failed to submit quiz'}, 500
        finally:
            conn.close()
from flask_restx import Namespace, Resource, fields
from flask import request
from controllers.auth_controller import auth_required
from database.db import get_db_connection

dashboard_ns = Namespace('dashboard', description='Dashboard operations')

# Models
quiz_attempt_model = dashboard_ns.model('QuizAttempt', {
    'id': fields.Integer(description='Quiz attempt ID'),
    'topic': fields.String(description='Quiz topic'),
    'date': fields.String(description='Date of attempt'),
    'score': fields.Integer(description='Score obtained'),
    'totalQuestions': fields.Integer(description='Total number of questions'),
    'status': fields.String(description='Quiz status (completed/incomplete)')
})

stats_model = dashboard_ns.model('DashboardStats', {
    'totalQuizzes': fields.Integer(description='Total number of quizzes attempted'),
    'averageScore': fields.Float(description='Average score percentage'),
    'highestScore': fields.Integer(description='Highest score percentage'),
    'lowestScore': fields.Integer(description='Lowest score percentage')
})

dashboard_response = dashboard_ns.model('DashboardResponse', {
    'recentQuizzes': fields.List(fields.Nested(quiz_attempt_model)),
    'stats': fields.Nested(stats_model)
})

@dashboard_ns.route('/stats')
class DashboardStats(Resource):
    @auth_required
    @dashboard_ns.response(200, 'Success', dashboard_response)
    @dashboard_ns.response(401, 'Unauthorized')
    def get(self):
        token = request.headers.get('Authorization')
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get user_id from token
            cursor.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
            user_data = cursor.fetchone()
            if not user_data:
                return {'message': 'Invalid token'}, 401
                
            user_id = user_data['user_id']
            
            # Get recent quizzes
            cursor.execute('''
                SELECT 
                    q.id,
                    q.topic,
                    q.created_at as date,
                    q.score,
                    q.total_questions,
                    q.status
                FROM quiz_attempts q
                WHERE q.user_id = ?
                ORDER BY q.created_at DESC
                LIMIT 10
            ''', (user_id,))
            
            recent_quizzes = []
            for row in cursor.fetchall():
                recent_quizzes.append({
                    'id': row['id'],
                    'topic': row['topic'],
                    'date': row['date'],
                    'score': row['score'],
                    'totalQuestions': row['total_questions'],
                    'status': row['status']
                })
            
            # Calculate stats from all completed quizzes
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_score,
                    MAX(CAST(score AS FLOAT) / total_questions * 100) as max_score,
                    MIN(CAST(score AS FLOAT) / total_questions * 100) as min_score
                FROM quiz_attempts
                WHERE user_id = ? AND status = 'completed'
            ''', (user_id,))
            
            stats_row = cursor.fetchone()
            stats = {
                'totalQuizzes': stats_row['total'],
                'averageScore': round(stats_row['avg_score'] or 0, 1),
                'highestScore': round(stats_row['max_score'] or 0),
                'lowestScore': round(stats_row['min_score'] or 0)
            }
            
            return {
                'recentQuizzes': recent_quizzes,
                'stats': stats
            }, 200
            
        finally:
            conn.close()
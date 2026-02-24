from flask_restx import Namespace, Resource
from flask import request
from database.db import get_db_connection
from controllers.auth_controller import auth_required
from datetime import datetime

debug_ns = Namespace('debug', description='Debug operations')

@debug_ns.route('/cleanup-quiz-data')
class CleanupQuizData(Resource):
    @auth_required
    def post(self):
        """Clean up quiz data by removing duplicates and fixing inconsistencies"""
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
            
            # Start transaction
            conn.execute('BEGIN TRANSACTION')
            
            # 1. Get all quiz topics for the user
            cursor.execute('''
                SELECT DISTINCT topic 
                FROM quiz_attempts 
                WHERE user_id = ?
            ''', (user_id,))
            topics = [row['topic'] for row in cursor.fetchall()]
            
            for topic in topics:
                # 2. For each topic, find the latest completed quiz
                cursor.execute('''
                    SELECT id 
                    FROM quiz_attempts 
                    WHERE user_id = ? AND topic = ? AND status = 'completed'
                    ORDER BY completed_at DESC 
                    LIMIT 1
                ''', (user_id, topic))
                completed = cursor.fetchone()
                
                if completed:
                    # 3. Delete all other quizzes for this topic
                    cursor.execute('''
                        DELETE FROM quiz_attempts 
                        WHERE user_id = ? AND topic = ? AND id != ?
                    ''', (user_id, topic, completed['id']))
                else:
                    # 4. If no completed quiz, keep only the latest incomplete quiz
                    cursor.execute('''
                        WITH LatestIncomplete AS (
                            SELECT id 
                            FROM quiz_attempts 
                            WHERE user_id = ? AND topic = ? AND status = 'incomplete'
                            ORDER BY created_at DESC 
                            LIMIT 1
                        )
                        DELETE FROM quiz_attempts 
                        WHERE user_id = ? AND topic = ? 
                        AND id NOT IN (SELECT id FROM LatestIncomplete)
                    ''', (user_id, topic, user_id, topic))
            
            # Commit transaction
            conn.commit()
            
            return {'message': 'Quiz data cleaned up successfully'}, 200
            
        except Exception as e:
            conn.rollback()
            print(f"Error cleaning up quiz data: {str(e)}")
            return {'error': 'Failed to clean up quiz data'}, 500
        finally:
            conn.close()
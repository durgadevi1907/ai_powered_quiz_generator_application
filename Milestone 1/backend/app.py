from flask import Flask, jsonify, send_from_directory
from flask_restx import Api
from flask_cors import CORS
import os
from database.db import init_db

def create_app():
    app = Flask(__name__)
    # Initialize the database
    init_db()
    
    @app.errorhandler(Exception)
    def handle_error(e):
        app.logger.error(f'An error occurred: {str(e)}')
        return {'message': 'An internal error occurred', 'error': str(e)}, 500
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configure single API with multiple namespaces
    api = Api(
        app,
        version='1.0',
        title='Quizomania API',
        description='Complete API for Quizomania including Authentication and Quiz Generation',
        doc='/swagger/',
        prefix='/api'
    )
    
    # Import and add authentication namespace
    from routes.auth_routes import auth_ns
    api.add_namespace(auth_ns, path='/auth')
    
    # Import and add questions namespace if Gemini is available
    try:
        from routes.question_routes import questions_ns
        api.add_namespace(questions_ns, path='/questions')
    except Exception as e:
        app.logger.warning(f"Could not initialize question routes: {e}")
    
    # Basic test route
    @app.route('/')
    def home():
        return jsonify({"message": "Quizomania API is running!", "status": "success"})

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting server on http://localhost:5000")
    print("Available routes:")
    print("  - GET  /")
    print("\nAPI Routes:")
    print("Authentication:")
    print("  - POST /api/auth/register")
    print("  - POST /api/auth/login")
    print("  - POST /api/auth/logout")
    print("\nQuestion Generation:")
    print("  - POST /api/questions/generate  (Generate quiz questions)")
    print("\nAPI Documentation:")
    print("  - GET  /swagger/  (Complete API documentation)")
    app.run(debug=True, host='0.0.0.0', port=5000)
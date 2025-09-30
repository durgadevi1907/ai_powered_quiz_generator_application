from flask import Flask, jsonify
from flask_restx import Api
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Test route
    @app.route('/')
    def home():
        return jsonify({"message": "AI Quiz Generator API is running!", "status": "success"})
    
    @app.route('/api/test')
    def test():
        return jsonify({"message": "API test route is working!"})
    
    # Configure API
    api = Api(
        app,
        version='1.0',
        title='Quizomania',
        description='A REST API for generating quiz questions using AI',
        doc='/swagger/'  # Swagger UI documentation
    )
    
    # Import and add namespaces
    from routes.question_routes import questions_ns
    api.add_namespace(questions_ns, path='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting server on http://localhost:5000")
    print("Available routes:")
    print("  - GET  /")
    print("  - GET  /api/test")
    print("  - POST /api/generate-questions")
    print("  - GET  /swagger/")
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask_restx import fields

def create_auth_models(api):
    register_model = api.model('Register', {
        'username': fields.String(required=True, description='Username'),
        'password': fields.String(required=True, description='Password')
    })

    login_model = api.model('Login', {
        'username': fields.String(required=True, description='Username'),
        'password': fields.String(required=True, description='Password')
    })

    auth_response = api.model('AuthResponse', {
        'message': fields.String(description='Response message'),
        'token': fields.String(description='Authentication token')
    })

    return register_model, login_model, auth_response
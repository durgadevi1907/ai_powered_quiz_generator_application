from flask_restx import Namespace, fields
from controllers.auth_controller import Register, Login, Logout

auth_ns = Namespace('auth', description='Authentication operations')

# Create models directly
register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

auth_response = auth_ns.model('AuthResponse', {
    'message': fields.String(required=True, description='Response message'),
    'token': fields.String(required=False, description='Authentication token')
})

# Add routes
auth_ns.add_resource(Register, '/register', 
    resource_class_args=(auth_ns, register_model, auth_response))
auth_ns.add_resource(Login, '/login',
    resource_class_args=(auth_ns, login_model, auth_response))
auth_ns.add_resource(Logout, '/logout',
    resource_class_args=(auth_ns, auth_response))
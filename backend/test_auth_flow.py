import requests
import os
from time import sleep

BASE_URL = 'http://localhost:5000/api/auth'

def test_auth_flow():
    # Generate a unique username for testing
    test_username = f'testuser_{os.urandom(4).hex()}'
    test_password = 'testpass123'
    
    print("\n=== Testing Authentication Flow ===\n")
    
    # 1. Register a new user
    print("1. REGISTER API")
    print(f"Endpoint: POST {BASE_URL}/register")
    print("Request Body:")
    print("""{
    "username": "<username>",
    "password": "<password>"
}""")
    
    register_response = requests.post(
        f'{BASE_URL}/register',
        json={
            'username': test_username,
            'password': test_password
        }
    )
    print("\nResponse:", register_response.status_code)
    print(register_response.json())
    
    if register_response.status_code != 201:
        print("Registration failed!")
        return
        
    print("\n" + "="*50 + "\n")
    
    # 2. Login with the registered user
    print("2. LOGIN API")
    print(f"Endpoint: POST {BASE_URL}/login")
    print("Request Body:")
    print("""{
    "username": "<username>",
    "password": "<password>"
}""")
    
    login_response = requests.post(
        f'{BASE_URL}/login',
        json={
            'username': test_username,
            'password': test_password
        }
    )
    print("\nResponse:", login_response.status_code)
    print(login_response.json())
    
    if login_response.status_code != 200:
        print("Login failed!")
        return
        
    token = login_response.json().get('token')
    
    print("\n" + "="*50 + "\n")
    
    # 3. Logout using the token
    print("3. LOGOUT API")
    print(f"Endpoint: POST {BASE_URL}/logout")
    print("Headers required:")
    print("""{
    "Authorization": "<token>"
}""")
    
    logout_response = requests.post(
        f'{BASE_URL}/logout',
        headers={'Authorization': token}
    )
    print("\nResponse:", logout_response.status_code)
    print(logout_response.json())
    
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_auth_flow()
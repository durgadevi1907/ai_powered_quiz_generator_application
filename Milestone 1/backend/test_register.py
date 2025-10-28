import requests
import sys
import os

def test_registration():
    url = 'http://localhost:5000/api/auth/register'
    data = {
        'username': f'testuser{os.urandom(4).hex()}',  # Generate unique username
        'password': 'testpass123'
    }
    
    try:
        print(f'Sending POST request to {url}')
        print(f'Request data: {data}')
        
        response = requests.post(url, json=data)
        print('\nResponse Status:', response.status_code)
        
        try:
            json_response = response.json()
            print('Response Body:', json_response)
            if response.status_code == 201:
                print('\nRegistration successful!')
                return True
            else:
                print('\nRegistration failed.')
                return False
        except ValueError:
            print('Raw Response:', response.text)
            return False
            
    except requests.exceptions.ConnectionError as e:
        print('Connection Error: Could not connect to server')
        print('Error details:', str(e))
        return False
    except Exception as e:
        print('Error:', str(e))
        return False

if __name__ == '__main__':
    if test_registration():
        sys.exit(0)
    else:
        sys.exit(1)
# debug_routes.py
import requests

BASE_URL = "http://localhost:5000"

def test_routes():
    try:
        # Test home route
        print("Testing home route...")
        response = requests.get(f"{BASE_URL}/")
        print(f"Home route: {response.status_code} - {response.json()}")
        
        # Test API test route
        print("\nTesting API test route...")
        response = requests.get(f"{BASE_URL}/api/test")
        print(f"API test route: {response.status_code} - {response.json()}")
        
        # Test questions test route
        print("\nTesting questions test route...")
        response = requests.get(f"{BASE_URL}/api/questions/test")
        print(f"Questions test route: {response.status_code} - {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("Server is not running. Please start the server first.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_routes()
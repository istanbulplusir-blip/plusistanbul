import requests
import json

def test_backend_direct():
    """Test backend API directly"""
    print("Testing backend directly...")
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login/',
            json={
                "username": "test",
                "password": "test123"
            }
        )
        print(f"Backend Status: {response.status_code}")
        print(f"Backend Response: {json.dumps(response.json() if response.ok else response.text, indent=2)}")
    except requests.exceptions.ConnectionError:
        print("Backend connection failed - Is Django server running?")

def test_through_nextjs():
    """Test through Next.js API route"""
    print("\nTesting through Next.js...")
    try:
        response = requests.post(
            'http://localhost:3001/api/v1/auth/login/',
            json={
                "username": "test",
                "password": "test123"
            }
        )
        print(f"Next.js Status: {response.status_code}")
        print(f"Next.js Response: {json.dumps(response.json() if response.ok else response.text, indent=2)}")
    except requests.exceptions.ConnectionError:
        print("Next.js connection failed - Is Next.js server running?")

if __name__ == '__main__':
    test_backend_direct()
    test_through_nextjs()

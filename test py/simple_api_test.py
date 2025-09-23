import requests
import json

# Test the API endpoint
url = "http://localhost:8000/api/transfers/routes/d7a77a78-c533-40cf-9bca-485ea046b656/calculate_price/"
data = {
    "vehicle_type": "sedan",
    "trip_type": "one_way", 
    "booking_time": "14:30",
    "selected_options": [
        {"option_id": "6d359c8b-2d2a-4ef2-ab16-cd324c65897f", "quantity": 1},
        {"option_id": "a110a073-dada-42bb-8bce-09f2d39b0b18", "quantity": 1}
    ]
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}") 
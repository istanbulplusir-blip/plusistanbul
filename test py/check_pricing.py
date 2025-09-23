#!/usr/bin/env python
import requests
import json

# Test pricing API
response = requests.get('http://127.0.0.1:8000/api/v1/events/events/')
data = response.json()

print("Event Pricing Check:")
print("=" * 50)

for event in data['results']:
    title = event.get('title', 'Unknown')
    min_price = event.get('min_price')
    max_price = event.get('max_price')
    
    print(f"Event: {title}")
    print(f"  Min Price: {min_price}")
    print(f"  Max Price: {max_price}")
    print()

print("All events processed successfully!") 
#!/usr/bin/env python
"""
Simple test script for transfer API endpoints.
"""

import os
import sys
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from transfers.models import TransferRoute, TransferRoutePricing, TransferOption

def test_transfer_api():
    """Test transfer API endpoints."""
    print("=" * 80)
    print("TRANSFER API TEST")
    print("=" * 80)
    
    # Create API client
    client = APIClient()
    
    # Test 1: Get all routes
    print("\n1. Testing GET /api/transfers/routes/")
    response = client.get('/api/transfers/routes/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} routes")
        for route in data[:3]:  # Show first 3 routes
            print(f"  - {route.get('origin')} → {route.get('destination')}")
    else:
        print(f"Error: {response.text}")
    
    # Test 2: Get specific route
    print("\n2. Testing GET /api/transfers/routes/{slug}/")
    routes = TransferRoute.objects.all()
    if routes.exists():
        route = routes.first()
        response = client.get(f'/api/transfers/routes/{route.slug}/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Route: {data.get('origin')} → {data.get('destination')}")
            print(f"Pricing options: {len(data.get('pricing', []))}")
        else:
            print(f"Error: {response.text}")
    
    # Test 3: Get pricing for a route
    print("\n3. Testing GET /api/transfers/routes/{slug}/pricing/")
    if routes.exists():
        route = routes.first()
        response = client.get(f'/api/transfers/routes/{route.slug}/pricing/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} pricing options")
            for pricing in data[:3]:  # Show first 3 pricing options
                print(f"  - {pricing.get('vehicle_type')}: ${pricing.get('base_price')}")
        else:
            print(f"Error: {response.text}")
    
    # Test 4: Get transfer options
    print("\n4. Testing GET /api/transfers/options/")
    response = client.get('/api/transfers/options/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} options")
        for option in data:
            print(f"  - {option.get('option_type')}: ${option.get('price')}")
    else:
        print(f"Error: {response.text}")
    
    # Test 5: Calculate pricing
    print("\n5. Testing POST /api/transfers/calculate-price/")
    if routes.exists():
        route = routes.first()
        pricing = TransferRoutePricing.objects.filter(route=route).first()
        if pricing:
            payload = {
                'route_slug': route.slug,
                'vehicle_type': pricing.vehicle_type,
                'passenger_count': 2,
                'luggage_count': 2,
                'trip_type': 'one_way',
                'outbound_date': '2024-12-25',
                'outbound_time': '14:00',
                'selected_options': []
            }
            response = client.post('/api/transfers/calculate-price/', payload, format='json')
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Base price: ${data.get('base_price')}")
                print(f"Final price: ${data.get('final_price')}")
            else:
                print(f"Error: {response.text}")
    
    print("\n" + "=" * 80)
    print("TRANSFER API TEST COMPLETED")
    print("=" * 80)

if __name__ == '__main__':
    test_transfer_api() 
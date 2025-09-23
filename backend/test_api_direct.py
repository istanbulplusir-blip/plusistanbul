#!/usr/bin/env python
import requests
import json

def test_api():
    try:
        # Test hero slides API
        response = requests.get('http://localhost:8000/api/v1/shared/hero-slides/active/')
        print(f'Status Code: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print(f'Number of slides: {len(data)}')

            for i, slide in enumerate(data):
                print(f'\nSlide {i+1}:')
                print(f'  ID: {slide["id"]}')
                print(f'  Title: {slide.get("title", "N/A")}')
                print(f'  Desktop Image URL: {slide.get("desktop_image_url", "N/A")}')
                print(f'  Has desktop image: {slide.get("desktop_image") is not None}')
        else:
            print(f'Error response: {response.text}')

    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_api()

#!/usr/bin/env python
"""
Generate a secure SECRET_KEY for Django production use.
Run this script and copy the output to your .env file.
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*60)
    print("Generated Django SECRET_KEY:")
    print("="*60)
    print(f"\nSECRET_KEY={secret_key}")
    print("\n" + "="*60)
    print("Copy the above line to your .env file")
    print("="*60 + "\n")

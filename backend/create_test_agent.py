#!/usr/bin/env python
"""
Create test agent for car rentals.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from agents.models import Agent
from users.models import User

def create_test_agent():
    """Create a test agent."""
    # Create user first
    user, user_created = User.objects.get_or_create(
        username='testagent',
        defaults={
            'email': 'test@agent.com',
            'first_name': 'Test',
            'last_name': 'Agent',
            'is_active': True,
        }
    )
    
    if user_created:
        print(f"Created user: {user.username}")
    
    # Create agent
    agent, created = Agent.objects.get_or_create(
        company_name='Test Agent Company',
        defaults={
            'user': user,
            'email': 'test@agent.com',
            'phone': '+1234567890',
            'is_active': True,
        }
    )
    
    if created:
        print(f"Created agent: {agent.company_name} (ID: {agent.id})")
    else:
        print(f"Agent already exists: {agent.company_name} (ID: {agent.id})")
    
    return agent

if __name__ == '__main__':
    agent = create_test_agent()
    print(f"Agent ID: {agent.id}")

#!/usr/bin/env python3
"""
Debug script to test the API endpoint and identify the 500 error
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/bandaskapp')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandaskapp.settings')
django.setup()

from django.test import RequestFactory
from core.views import api_status
from hardware.controller import HardwareController

def test_api_status():
    """Test the API status endpoint"""
    print("Testing API status endpoint...")
    print("=" * 50)
    
    try:
        # Test the controller directly first
        print("1. Testing HardwareController.get_system_status()...")
        controller = HardwareController()
        status = controller.get_system_status()
        print(f"   Status: {status}")
        print()
        
        # Test the API view
        print("2. Testing API status view...")
        factory = RequestFactory()
        request = factory.get('/api/status/')
        
        response = api_status(request)
        print(f"   Response status: {response.status_code}")
        print(f"   Response content: {response.content.decode()}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api_status()

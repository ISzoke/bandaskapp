#!/usr/bin/env python3
"""
Test script to verify heating controller status API
"""
import requests
import json

def test_heating_controller_api():
    """Test the heating controller API endpoints"""
    base_url = "http://localhost:8080"
    
    print("Testing Heating Controller API...")
    print("=" * 50)
    
    # Test 1: Get digital input status
    try:
        url = f"{base_url}/json/di/1_01"  # HEATING_CONTROL_UNIT_ID
        print(f"GET {url}")
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            value = data.get('value', 0)
            print(f"Heating Controller State: {'ON' if value else 'OFF'}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 2: Set digital input to ON
    try:
        url = f"{base_url}/json/di/1_01"
        payload = {"value": 1}
        print(f"POST {url} with payload {payload}")
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 3: Get status again to verify change
    try:
        url = f"{base_url}/json/di/1_01"
        print(f"GET {url} (after setting to ON)")
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            value = data.get('value', 0)
            print(f"Heating Controller State: {'ON' if value else 'OFF'}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 4: Set digital input to OFF
    try:
        url = f"{base_url}/json/di/1_01"
        payload = {"value": 0}
        print(f"POST {url} with payload {payload}")
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test 5: Get status endpoint
    try:
        url = f"{base_url}/status"
        print(f"GET {url}")
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            heating_control = data.get('heating_control', {})
            print(f"Heating Control Info: {json.dumps(heating_control, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_heating_controller_api()

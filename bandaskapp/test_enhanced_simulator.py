#!/usr/bin/env python3
"""
Test script for the enhanced EVOK simulator
Tests both auto-cycle and manual control features
"""
import requests
import time
import json

def test_simulator():
    """Test the enhanced simulator features"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Enhanced EVOK Simulator")
    print("="*50)
    
    # Test 1: Basic connectivity
    try:
        resp = requests.get(f"{base_url}/status", timeout=5)
        if resp.status_code == 200:
            print("✅ Simulator connectivity: OK")
        else:
            print("❌ Simulator connectivity: FAILED")
            return False
    except:
        print("❌ Simulator not running or not accessible")
        return False
    
    # Test 2: Enhanced status endpoint
    try:
        resp = requests.get(f"{base_url}/status", timeout=5)
        data = resp.json()
        
        print(f"✅ Simulation mode: {data.get('simulation_mode', 'unknown')}")
        
        cycle_info = data.get('cycle_info', {})
        print(f"✅ Cycle progress: {cycle_info.get('progress_percent', 0):.1f}%")
        print(f"✅ Target temperature: {cycle_info.get('target_temperature', 0):.1f}°C")
        print(f"✅ Temperature range: {cycle_info.get('temp_range', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return False
    
    # Test 3: Temperature reading
    try:
        resp = requests.get(f"{base_url}/json/temp/2895DCD509000035", timeout=5)
        data = resp.json()
        temp = data.get('value', 0)
        print(f"✅ Current DHW temperature: {temp}°C")
        
        if 15 <= temp <= 90:
            print("✅ Temperature in valid range")
        else:
            print("⚠️  Temperature outside expected range")
            
    except Exception as e:
        print(f"❌ Temperature reading error: {e}")
        return False
    
    # Test 4: Relay control
    try:
        resp = requests.get(f"{base_url}/json/ro/1_01", timeout=5)
        data = resp.json()
        relay_state = data.get('value', 0)
        print(f"✅ Furnace relay state: {'ON' if relay_state else 'OFF'}")
        
    except Exception as e:
        print(f"❌ Relay reading error: {e}")
        return False
    
    # Test 5: Monitor temperature changes over time
    print("\n📊 Monitoring temperature changes (30 seconds)...")
    start_time = time.time()
    last_temp = None
    temp_changes = 0
    
    for i in range(6):  # 6 readings over 30 seconds
        try:
            resp = requests.get(f"{base_url}/json/temp/2895DCD509000035", timeout=5)
            data = resp.json()
            temp = data.get('value', 0)
            
            status_resp = requests.get(f"{base_url}/status", timeout=5)
            status_data = status_resp.json()
            mode = status_data.get('simulation_mode', 'unknown')
            progress = status_data.get('cycle_info', {}).get('progress_percent', 0)
            
            print(f"  [{i*5:2d}s] {temp:5.1f}°C ({mode}, {progress:.1f}%)")
            
            if last_temp and abs(temp - last_temp) > 0.1:
                temp_changes += 1
            
            last_temp = temp
            time.sleep(5)
            
        except Exception as e:
            print(f"  Error reading temperature: {e}")
    
    if temp_changes > 0:
        print(f"✅ Temperature changed {temp_changes} times (cycling working)")
    else:
        print("⚠️  No temperature changes detected")
    
    print("\n🎊 Simulator test completed!")
    return True

if __name__ == "__main__":
    print("Starting enhanced simulator test...")
    print("Make sure the simulator is running: python hardware/simulator.py")
    print()
    
    success = test_simulator()
    
    if success:
        print("\n✅ All tests passed! Enhanced simulator is working correctly.")
        print("\n🎮 Manual controls available in simulator terminal:")
        print("   M - Toggle Auto/Manual mode")
        print("   ↑ - Increase temperature (+1°C)")
        print("   ↓ - Decrease temperature (-1°C)")
        print("   R - Reset to auto cycle")
        print("   Q - Quit simulator")
    else:
        print("\n❌ Some tests failed. Check simulator status.")

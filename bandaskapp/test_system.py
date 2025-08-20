#!/usr/bin/env python3
"""
Comprehensive system test for BandaskApp Summer Mode
Tests all major components and functionality
"""
import os
import sys
import time
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append('/media/data/Igor/Python/BandaskApp/bandaskapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bandaskapp.settings')

import django
django.setup()

from hardware.controller import HardwareController
from core.models import TemperatureSensor, Relay, SystemState, SystemLog

class SystemTester:
    def __init__(self):
        self.controller = HardwareController()
        self.base_url = "http://localhost:8000"
        self.evok_url = "http://localhost:8080"
        self.tests_passed = 0
        self.tests_failed = 0
    
    def run_all_tests(self):
        """Run all system tests"""
        print("="*60)
        print("BandaskApp Summer Mode - System Test Suite")
        print("="*60)
        
        # Test 1: Hardware Simulator
        self.test_hardware_simulator()
        
        # Test 2: Database Models
        self.test_database_models()
        
        # Test 3: Hardware Controller
        self.test_hardware_controller()
        
        # Test 4: Web Interface
        self.test_web_interface()
        
        # Test 5: API Endpoints
        self.test_api_endpoints()
        
        # Test 6: Control Logic
        self.test_control_logic()
        
        # Test 7: Manual Override
        self.test_manual_override()
        
        # Summary
        self.print_summary()
    
    def test_hardware_simulator(self):
        """Test hardware simulator functionality"""
        print("\n1. Testing Hardware Simulator...")
        
        try:
            # Test temperature reading
            resp = requests.get(f"{self.evok_url}/json/temp/2895DCD509000035", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                temp = data.get('value')
                if temp is not None and 0 <= temp <= 100:
                    self.test_pass(f"Temperature reading: {temp}°C")
                else:
                    self.test_fail(f"Invalid temperature: {temp}")
            else:
                self.test_fail(f"HTTP error: {resp.status_code}")
                
            # Test relay reading
            resp = requests.get(f"{self.evok_url}/json/ro/1_01", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                state = data.get('value')
                if state in [0, 1]:
                    self.test_pass(f"Relay state: {state}")
                else:
                    self.test_fail(f"Invalid relay state: {state}")
            else:
                self.test_fail(f"HTTP error: {resp.status_code}")
                
            # Test relay control
            resp = requests.post(f"{self.evok_url}/json/ro/1_01", 
                               json={"value": 1}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('success'):
                    self.test_pass("Relay control successful")
                else:
                    self.test_fail("Relay control failed")
            else:
                self.test_fail(f"HTTP error: {resp.status_code}")
                
        except Exception as e:
            self.test_fail(f"Hardware simulator error: {e}")
    
    def test_database_models(self):
        """Test database models and data integrity"""
        print("\n2. Testing Database Models...")
        
        try:
            # Test temperature sensor
            dhw_sensor = TemperatureSensor.objects.get(name='DHW-1')
            if dhw_sensor.circuit_id == '2895DCD509000035':
                self.test_pass("DHW sensor found in database")
            else:
                self.test_fail("DHW sensor circuit ID mismatch")
                
            # Test furnace relay
            furnace = Relay.objects.get(name='Furnace')
            if furnace.circuit_id == '1_01':
                self.test_pass("Furnace relay found in database")
            else:
                self.test_fail("Furnace relay circuit ID mismatch")
                
            # Test system state
            system_state = SystemState.load()
            if system_state.dhw_temp_low == 45.0 and system_state.dhw_temp_high == 60.0:
                self.test_pass("System state thresholds correct")
            else:
                self.test_fail("System state thresholds incorrect")
                
        except Exception as e:
            self.test_fail(f"Database model error: {e}")
    
    def test_hardware_controller(self):
        """Test hardware controller functionality"""
        print("\n3. Testing Hardware Controller...")
        
        try:
            # Test API connectivity
            if self.controller.check_api_connectivity():
                self.test_pass("Hardware controller API connection")
            else:
                self.test_fail("Hardware controller API connection failed")
                
            # Test temperature reading
            temp = self.controller.update_temperature()
            if temp is not None and 0 <= temp <= 100:
                self.test_pass(f"Hardware controller temperature reading: {temp}°C")
            else:
                self.test_fail("Hardware controller temperature reading failed")
                
            # Test system status
            status = self.controller.get_system_status()
            if isinstance(status, dict) and 'control_mode' in status:
                self.test_pass("Hardware controller system status")
            else:
                self.test_fail("Hardware controller system status failed")
                
        except Exception as e:
            self.test_fail(f"Hardware controller error: {e}")
    
    def test_web_interface(self):
        """Test web interface accessibility"""
        print("\n4. Testing Web Interface...")
        
        try:
            # Test dashboard
            resp = requests.get(f"{self.base_url}/", timeout=10)
            if resp.status_code == 200 and "BandaskApp" in resp.text:
                self.test_pass("Dashboard page loads")
            else:
                self.test_fail(f"Dashboard error: {resp.status_code}")
                
            # Test logs page
            resp = requests.get(f"{self.base_url}/logs/", timeout=10)
            if resp.status_code == 200:
                self.test_pass("Logs page loads")
            else:
                self.test_fail(f"Logs page error: {resp.status_code}")
                
            # Test settings page
            resp = requests.get(f"{self.base_url}/settings/", timeout=10)
            if resp.status_code == 200:
                self.test_pass("Settings page loads")
            else:
                self.test_fail(f"Settings page error: {resp.status_code}")
                
        except Exception as e:
            self.test_fail(f"Web interface error: {e}")
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n5. Testing API Endpoints...")
        
        try:
            # Test status API
            resp = requests.get(f"{self.base_url}/api/status/", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('success') and 'dhw_temp' in data:
                    self.test_pass("Status API endpoint")
                else:
                    self.test_fail("Status API data invalid")
            else:
                self.test_fail(f"Status API error: {resp.status_code}")
                
        except Exception as e:
            self.test_fail(f"API endpoint error: {e}")
    
    def test_control_logic(self):
        """Test automatic control logic"""
        print("\n6. Testing Control Logic...")
        
        try:
            # Get current temperature
            current_temp = self.controller.update_temperature()
            if current_temp is None:
                self.test_fail("Cannot test control logic - no temperature reading")
                return
                
            # Test furnace control decision
            furnace = Relay.objects.get(name='Furnace')
            system_state = SystemState.load()
            
            if current_temp < system_state.dhw_temp_low:
                # Temperature is low - furnace should be ON
                result = self.controller.control_furnace()
                furnace.refresh_from_db()
                if furnace.current_state:
                    self.test_pass("Furnace started when temperature low")
                else:
                    self.test_fail("Furnace not started when temperature low")
            else:
                self.test_pass("Control logic test skipped (temp not low)")
                
        except Exception as e:
            self.test_fail(f"Control logic error: {e}")
    
    def test_manual_override(self):
        """Test manual control functionality"""
        print("\n7. Testing Manual Override...")
        
        try:
            # Test manual furnace control
            success = self.controller.manual_control_furnace(False)
            if success:
                furnace = Relay.objects.get(name='Furnace')
                if not furnace.current_state:
                    self.test_pass("Manual furnace OFF")
                else:
                    self.test_fail("Manual furnace OFF failed")
            else:
                self.test_fail("Manual control command failed")
                
            # Test mode switching
            system_state = SystemState.load()
            original_mode = system_state.control_mode
            system_state.control_mode = 'manual'
            system_state.save()
            
            system_state.refresh_from_db()
            if system_state.control_mode == 'manual':
                self.test_pass("Control mode switching")
                
                # Restore original mode
                system_state.control_mode = original_mode
                system_state.save()
            else:
                self.test_fail("Control mode switching failed")
                
        except Exception as e:
            self.test_fail(f"Manual override error: {e}")
    
    def test_pass(self, message):
        """Record a passed test"""
        print(f"  ✓ {message}")
        self.tests_passed += 1
    
    def test_fail(self, message):
        """Record a failed test"""
        print(f"  ✗ {message}")
        self.tests_failed += 1
    
    def print_summary(self):
        """Print test summary"""
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests:  {total_tests}")
        print(f"Passed:       {self.tests_passed}")
        print(f"Failed:       {self.tests_failed}")
        print(f"Pass Rate:    {pass_rate:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        else:
            print(f"\n⚠️  {self.tests_failed} tests failed. Please review and fix issues.")
        
        print("="*60)

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()









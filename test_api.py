#!/usr/bin/env python3
"""
Test script for the Temperature Monitoring API
Run this to verify your API is working correctly
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5001"  # Change to your Pi Zero IP if testing remotely

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_submit_temperature():
    """Test submitting temperature data"""
    print("\nTesting temperature submission...")
    
    data = {
        "sensor_name": "test_sensor",
        "temperature": 23.5,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/temperature",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_latest():
    """Test getting latest temperature"""
    print("\nTesting latest temperature retrieval...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/temperature/latest?sensor_name=test_sensor")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_history():
    """Test getting historical data"""
    print("\nTesting historical data retrieval...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/temperature/history?sensor_name=test_sensor&hours=24")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_sensors():
    """Test getting sensor list"""
    print("\nTesting sensor list retrieval...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/sensors")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("Temperature Monitoring API Test")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Submit Temperature", test_submit_temperature),
        ("Get Latest", test_get_latest),
        ("Get History", test_get_history),
        ("Get Sensors", test_get_sensors)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        print(f"Running: {test_name}")
        print(f"{'='*20}")
        
        success = test_func()
        results.append((test_name, success))
        
        if not success:
            print(f"❌ {test_name} FAILED")
        else:
            print(f"✅ {test_name} PASSED")
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*40}")
    print("TEST SUMMARY")
    print(f"{'='*40}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your setup and try again.")

if __name__ == "__main__":
    main() 
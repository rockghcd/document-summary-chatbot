"""
Test script for Document Summary Chatbot
Tests basic functionality without requiring OpenAI API
"""

import requests
import json
import os

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            print(f"   AI Available: {data['ai_available']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_home_page():
    """Test the home page loads"""
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("✅ Home page loads successfully")
            return True
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return False

def test_invalid_endpoint():
    """Test 404 handling"""
    try:
        response = requests.get('http://localhost:5000/nonexistent')
        if response.status_code == 404:
            print("✅ 404 error handling works")
            return True
        else:
            print(f"❌ 404 handling failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 404 test error: {e}")
        return False

def test_chat_endpoint_without_data():
    """Test chat endpoint with invalid data"""
    try:
        response = requests.post('http://localhost:5000/chat', 
                               json={})
        if response.status_code == 400:
            print("✅ Chat endpoint validates input correctly")
            return True
        else:
            print(f"❌ Chat validation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Document Summary Chatbot...")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_home_page,
        test_invalid_endpoint,
        test_chat_endpoint_without_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready.")
    else:
        print("⚠️  Some tests failed. Check the application setup.")

if __name__ == "__main__":
    main() 
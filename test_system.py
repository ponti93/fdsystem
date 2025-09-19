#!/usr/bin/env python3
"""
System Test Script
Tests if the fraud detection system is running properly
"""

import requests
import time
import json
from datetime import datetime

def test_backend():
    """Test if backend is running"""
    try:
        print("🔍 Testing backend API...")
        
        # Test health endpoint
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
            print(f"   Timestamp: {health_data.get('timestamp')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_frontend():
    """Test if frontend is running"""
    try:
        print("\n🔍 Testing frontend...")
        
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running!")
            return True
        else:
            print(f"❌ Frontend test failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def test_transaction_processing():
    """Test transaction processing"""
    try:
        print("\n🔍 Testing transaction processing...")
        
        test_transaction = {
            "amount": 150000,
            "user_id": 1,
            "merchant_id": "TEST_STORE",
            "currency": "NGN",
            "payment_method": "card",
            "ip_address": "192.168.1.100"
        }
        
        response = requests.post(
            'http://localhost:8000/api/transactions',
            json=test_transaction,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Transaction processing works!")
            
            if 'data' in result:
                fraud_data = result['data'].get('fraud_analysis', {})
                print(f"   Transaction ID: {result['data'].get('transaction_id')}")
                print(f"   Decision: {fraud_data.get('decision')}")
                print(f"   Fraud Score: {fraud_data.get('fraud_score')}")
                print(f"   Rules Triggered: {fraud_data.get('rules_triggered')}")
            
            return True
        else:
            print(f"❌ Transaction test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Transaction test error: {e}")
        return False

def test_flutterwave_integration():
    """Test Flutterwave integration"""
    try:
        print("\n🔍 Testing Flutterwave integration...")
        
        test_data = {
            "amount": 75000,
            "user_id": 1,
            "merchant_id": "FLUTTERWAVE_TEST",
            "currency": "NGN",
            "email": "test@example.com",
            "phone": "+2348012345678"
        }
        
        response = requests.post(
            'http://localhost:8000/api/flutterwave/test-webhook',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Flutterwave integration works!")
            
            if 'data' in result and 'fraud_analysis' in result['data']:
                fraud_data = result['data']['fraud_analysis']
                print(f"   Decision: {fraud_data.get('decision')}")
                print(f"   Fraud Score: {fraud_data.get('fraud_score')}")
            
            return True
        else:
            print(f"❌ Flutterwave test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Flutterwave test error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("🛡️  FRAUD DETECTION SYSTEM TEST")
    print("=" * 50)
    
    # Wait a moment for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    # Test backend
    backend_ok = test_backend()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Test transaction processing (only if backend is working)
    transaction_ok = False
    if backend_ok:
        transaction_ok = test_transaction_processing()
    
    # Test Flutterwave integration (only if backend is working)
    flutterwave_ok = False
    if backend_ok:
        flutterwave_ok = test_flutterwave_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Backend API:           {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Dashboard:    {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"Transaction Processing: {'✅ PASS' if transaction_ok else '❌ FAIL'}")
    print(f"Flutterwave Integration: {'✅ PASS' if flutterwave_ok else '❌ FAIL'}")
    
    if all([backend_ok, frontend_ok, transaction_ok, flutterwave_ok]):
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        print("\n🌐 Access your system:")
        print("   Frontend: http://localhost:3000")
        print("   Backend:  http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("\n🔐 Authentication:")
        print("   Admin:    admin_token123")
        print("   Analyst:  analyst_token123")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        
        if not backend_ok:
            print("\n🔧 To start backend:")
            print("   cd backend")
            print("   python main_simple.py")
            
        if not frontend_ok:
            print("\n🔧 To start frontend:")
            print("   cd frontend") 
            print("   npm start")

if __name__ == "__main__":
    main()

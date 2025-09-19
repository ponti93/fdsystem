#!/usr/bin/env python3
"""
Webhook Setup Script
Sets up ngrok tunnel and Flutterwave webhook configuration
"""

import os
import sys
import subprocess
import requests
import json
import time
from urllib.parse import urljoin

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ngrok found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ngrok not found")
            return False
    except FileNotFoundError:
        print("❌ Ngrok not installed")
        return False

def install_ngrok_instructions():
    """Provide ngrok installation instructions"""
    print("\n🔧 Ngrok Installation Instructions:")
    print("=" * 50)
    print("1. Download ngrok from: https://ngrok.com/download")
    print("2. Extract to a folder (e.g., C:\\ngrok\\)")
    print("3. Add to PATH or run from the extracted folder")
    print("4. Sign up for free account at: https://ngrok.com/signup")
    print("5. Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("6. Run: ngrok config add-authtoken YOUR_TOKEN")
    print("\nAlternatively, run this script after installing ngrok!")

def start_ngrok_tunnel():
    """Start ngrok tunnel for webhook testing"""
    try:
        print("\n🌐 Starting ngrok tunnel...")
        
        # Start ngrok in the background
        process = subprocess.Popen(
            ['ngrok', 'http', '8000', '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for ngrok to start
        print("⏳ Waiting for ngrok to initialize...")
        time.sleep(5)
        
        # Get the public URL
        try:
            tunnels_response = requests.get('http://localhost:4040/api/tunnels')
            if tunnels_response.status_code == 200:
                tunnels = tunnels_response.json()
                
                for tunnel in tunnels.get('tunnels', []):
                    if tunnel.get('proto') == 'https':
                        public_url = tunnel.get('public_url')
                        print(f"✅ Ngrok tunnel active: {public_url}")
                        return public_url, process
                
                print("❌ No HTTPS tunnel found")
                return None, process
            else:
                print("❌ Could not get tunnel information")
                return None, process
                
        except requests.exceptions.ConnectionError:
            print("❌ Ngrok API not accessible")
            return None, process
            
    except FileNotFoundError:
        print("❌ Ngrok not found. Please install ngrok first.")
        return None, None
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None, None

def create_webhook_config(public_url):
    """Create webhook configuration instructions"""
    webhook_url = f"{public_url}/api/webhooks/flutterwave"
    
    print(f"\n🔗 Webhook Configuration:")
    print("=" * 50)
    print(f"Webhook URL: {webhook_url}")
    print("\n📋 Flutterwave Dashboard Setup:")
    print("1. Go to: https://dashboard.flutterwave.com/settings/webhooks")
    print("2. Set Webhook URL:", webhook_url)
    print("3. Set Secret Hash: flutterwave_webhook_secret_123")
    print("4. Enable: charge.completed, charge.failed")
    print("5. Save settings")
    
    return webhook_url

def test_webhook_endpoint(public_url):
    """Test if webhook endpoint is accessible"""
    try:
        webhook_url = f"{public_url}/health"
        response = requests.get(webhook_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Webhook endpoint accessible: {webhook_url}")
            return True
        else:
            print(f"❌ Webhook endpoint returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook endpoint test failed: {e}")
        return False

def main():
    """Main webhook setup function"""
    print("🔗 FLUTTERWAVE WEBHOOK SETUP")
    print("=" * 50)
    print("This script helps you set up real Flutterwave webhooks for testing")
    print()
    
    # Check if ngrok is installed
    if not check_ngrok():
        install_ngrok_instructions()
        return
    
    # Start ngrok tunnel
    public_url, ngrok_process = start_ngrok_tunnel()
    
    if not public_url:
        print("❌ Failed to start ngrok tunnel")
        return
    
    # Test webhook endpoint
    if test_webhook_endpoint(public_url):
        webhook_url = create_webhook_config(public_url)
        
        print(f"\n🎉 SETUP COMPLETE!")
        print("=" * 50)
        print("Your fraud detection system is now accessible via:")
        print(f"Public URL: {public_url}")
        print(f"Webhook URL: {webhook_url}")
        print()
        print("🔧 Next Steps:")
        print("1. Configure the webhook URL in your Flutterwave dashboard")
        print("2. Test real payments using the payment interface")
        print("3. Watch real webhooks trigger fraud detection!")
        print()
        print("⚠️  Keep this script running to maintain the tunnel")
        print("Press Ctrl+C to stop the tunnel")
        
        try:
            # Keep the tunnel running
            ngrok_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping ngrok tunnel...")
            ngrok_process.terminate()
            print("✅ Tunnel stopped")
    
    else:
        if ngrok_process:
            ngrok_process.terminate()

if __name__ == "__main__":
    main()

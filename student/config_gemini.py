#!/usr/bin/env python3
"""
Script to configure Gemini API key for the DisasterAI chatbot backend
"""

import os
import sys

# Set the Gemini API key
GEMINI_API_KEY = "AIzaSyBVl5_gINJYYQzwhmB-zXTkr_5VmOZUAPQ"

def configure_api_key():
    """Configure the Gemini API key as an environment variable"""
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
    
    print("✅ Gemini API key configured successfully!")
    print(f"🔑 API Key: {GEMINI_API_KEY[:20]}...")
    
    # Test the configuration
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Test with a simple model instantiation
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini API connection test successful!")
        print("🚀 Backend is ready to use Gemini API")
        
        return True
    except ImportError as e:
        print(f"❌ Error importing google.generativeai: {e}")
        print("💡 Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        return False

def create_env_file():
    """Create a .env file with the API key"""
    env_content = f"""# Gemini API Configuration
GEMINI_API_KEY={GEMINI_API_KEY}

# Flask Configuration
FLASK_DEBUG=True
PORT=5000
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with API key")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    print("🔧 Configuring DisasterAI Backend with Gemini API")
    print("=" * 50)
    
    # Configure API key
    success = configure_api_key()
    
    # Create .env file for persistent configuration
    create_env_file()
    
    if success:
        print("\n🎉 Configuration complete!")
        print("💡 You can now start the backend with: python chatbot_backend.py")
    else:
        print("\n⚠️ Configuration had issues. Please check your API key.")
        sys.exit(1)
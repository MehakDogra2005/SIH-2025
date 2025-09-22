#!/usr/bin/env python3
"""
Test script to verify Gemini API integration with DisasterAI backend
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def test_gemini_integration():
    """Test the Gemini API integration"""
    try:
        # Import the backend components
        from chatbot_backend import DisasterPromptEngine, GeminiAPIHandler, ChatbotBackend
        
        print("🧪 Testing DisasterAI Backend Components")
        print("=" * 50)
        
        # Test 1: Check API key configuration
        print("1. Testing API key configuration...")
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            print(f"✅ API key found: {api_key[:20]}...")
        else:
            print("❌ API key not found in environment")
            return False
        
        # Test 2: Initialize Gemini handler
        print("\n2. Testing Gemini handler initialization...")
        gemini_handler = GeminiAPIHandler(api_key)
        if gemini_handler.is_available():
            print("✅ Gemini handler initialized successfully")
        else:
            print("❌ Gemini handler initialization failed")
            return False
        
        # Test 3: Test prompt engine
        print("\n3. Testing prompt engine...")
        prompt_engine = DisasterPromptEngine()
        test_message = "I need help with flood safety"
        message_type = prompt_engine.analyze_message_type(test_message)
        specialized_prompt = prompt_engine.create_specialized_prompt(test_message, message_type)
        print(f"✅ Message type detected: {message_type}")
        print(f"✅ Specialized prompt created (length: {len(specialized_prompt)} chars)")
        
        # Test 4: Test simple Gemini API call
        print("\n4. Testing Gemini API call...")
        simple_prompt = "You are DisasterAI. Respond with exactly: 'DisasterAI backend test successful!' nothing else."
        response = gemini_handler.process_text_request(simple_prompt)
        print(f"✅ Gemini API response: {response}")
        
        # Test 5: Test full backend integration
        print("\n5. Testing full backend integration...")
        backend = ChatbotBackend()
        test_result = backend.process_chat_request(
            "Help me prepare for earthquakes",
            files=None,
            context={"inputMethod": "test", "sessionId": "test-123"},
            preferences={"responseStyle": "supportive"}
        )
        
        if test_result.get('success'):
            print("✅ Full backend integration test successful")
            print(f"📝 Response preview: {test_result['response'][:100]}...")
            print(f"🔍 Message type: {test_result.get('message_type')}")
        else:
            print(f"❌ Backend integration test failed: {test_result.get('error')}")
            return False
        
        print("\n🎉 All tests passed! Backend is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 DisasterAI Backend Integration Test")
    print("=" * 50)
    
    success = test_gemini_integration()
    
    if success:
        print("\n✅ Integration test completed successfully!")
        print("💡 You can now start the backend server with confidence.")
    else:
        print("\n❌ Integration test failed!")
        print("🔧 Please check the configuration and try again.")
        sys.exit(1)
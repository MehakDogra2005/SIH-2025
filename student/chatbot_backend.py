"""
Disaster Management Chatbot Backend
Handles user messages with specialized prompts and integrates with Gemini API
"""

import os
import json
import base64
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from io import BytesIO
import mimetypes
import functools

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    print("❌ google-generativeai not installed. Run: pip install google-generativeai")
    genai = None

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

try:
    from PIL import Image
except ImportError:
    print("❌ Pillow not installed. Run: pip install pillow")
    Image = None

try:
    import PyPDF2
except ImportError:
    print("❌ PyPDF2 not installed. Run: pip install PyPDF2")
    PyPDF2 = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

def run_async(func):
    """Decorator to run async functions in sync context"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

class DisasterPromptEngine:
    """Manages specialized prompts for different disaster scenarios and content types"""
    
    def __init__(self):
        self.base_context = """You are DisasterAI, a friendly and helpful assistant specializing in disaster management, emergency guidance, and safety support.

COMMUNICATION STYLE:
- Be natural, warm, and conversational
- Match the user's tone - casual for greetings, serious for emergencies
- Keep responses concise unless detailed information is needed
- Use simple, clear language
- Be supportive and reassuring

CORE CAPABILITIES:
- Emergency safety guidance and protocols
- Disaster preparedness education
- Psychological support during stressful situations
- Resource connections and emergency contacts
- Image/video analysis for damage assessment

RESPONSE APPROACH:
- For casual greetings: Respond naturally and ask how you can help
- For emergencies: Provide immediate, actionable safety guidance
- For questions: Give clear, helpful information
- Always prioritize user safety and well-being
"""
        
        self.specialized_prompts = {
            "text_only": """
USER MESSAGE: {user_message}

INSTRUCTIONS:
- If this is a simple greeting (hello, hi, hey, etc.), respond warmly and briefly, then ask how you can help with disaster preparedness or safety
- If this is an emergency, provide immediate safety guidance
- If this is a question about disaster news, updates, or current situations, provide helpful information while clarifying that you cannot access real-time data
- If this is a general question, provide helpful, clear information
- Keep the tone conversational and match the user's energy level
- Be concise unless detailed information is specifically requested

Provide a natural, helpful response.
""",

            "disaster_information": """
CONTEXT: User is asking for information, news, or updates about disaster situations, weather conditions, or emergency events.

IMPORTANT: You do not have access to real-time data, current news, or live updates. Be honest about this limitation.

RESPONSE APPROACH:
1. ACKNOWLEDGE REQUEST - Recognize their information need
2. EXPLAIN LIMITATIONS - Clarify you don't have real-time data
3. PROVIDE GUIDANCE - Suggest reliable sources for current information
4. OFFER PREPAREDNESS HELP - Provide relevant safety information
5. EMERGENCY CONTEXT - Include emergency contact info if relevant

RESPONSE FORMAT:
📰 INFORMATION REQUEST: [Acknowledge what they're asking about]
⚠️ REAL-TIME LIMITATION: [Explain you don't have current data]
🔍 RELIABLE SOURCES: [Suggest where to get current information]
💡 PREPAREDNESS GUIDANCE: [Relevant safety tips for the situation]
📞 EMERGENCY CONTACTS: [If situation might be relevant]

USER MESSAGE: {user_message}

Provide helpful guidance while being transparent about your limitations regarding real-time information.
""",
            
            "image_analysis": """
CONTEXT: User has shared an image that may show disaster conditions, damage, or emergency situations.

ANALYSIS TASKS:
1. SAFETY ASSESSMENT - Identify immediate dangers or hazards visible
2. SITUATION EVALUATION - Assess severity and urgency level
3. ACTIONABLE GUIDANCE - Provide specific next steps
4. PSYCHOLOGICAL SUPPORT - Acknowledge stress and provide reassurance
5. EMERGENCY PROTOCOLS - Reference relevant emergency procedures

RESPONSE FORMAT:
🚨 IMMEDIATE SAFETY: [Key safety points]
📊 SITUATION ASSESSMENT: [What you observe]
✅ RECOMMENDED ACTIONS: [Step-by-step guidance]
💭 PSYCHOLOGICAL SUPPORT: [Calming, supportive message]
📞 EMERGENCY CONTACTS: [If situation warrants]

USER MESSAGE (with image): {user_message}

Analyze the image and provide comprehensive disaster management guidance.
""",
            
            "video_analysis": """
CONTEXT: User has shared a video that may show dynamic disaster conditions, evacuation scenarios, or emergency situations in progress.

ANALYSIS TASKS:
1. MOTION & DYNAMICS - Assess movement, progression of conditions
2. SAFETY HAZARDS - Identify immediate and developing dangers
3. EVACUATION ASSESSMENT - Evaluate escape routes and safety options
4. EMERGENCY RESPONSE - Determine if immediate emergency services needed
5. PSYCHOLOGICAL IMPACT - Address potential trauma and stress

RESPONSE FORMAT:
🎥 VIDEO ASSESSMENT: [Key observations from video]
⚠️ IMMEDIATE RISKS: [Dangers identified]
🏃 EVACUATION GUIDANCE: [Movement and safety instructions]
📱 EMERGENCY RESPONSE: [When to call emergency services]
🧠 PSYCHOLOGICAL SUPPORT: [Trauma-informed support]

USER MESSAGE (with video): {user_message}

Analyze the video content and provide dynamic disaster response guidance.
""",
            
            "pdf_analysis": """
CONTEXT: User has shared a PDF document that may contain emergency plans, safety procedures, incident reports, or preparedness materials.

ANALYSIS TASKS:
1. DOCUMENT TYPE - Identify the nature and purpose of the document
2. KEY INFORMATION - Extract critical safety and emergency information
3. PROCEDURE REVIEW - Assess emergency procedures for completeness
4. RECOMMENDATIONS - Suggest improvements or additional measures
5. IMPLEMENTATION GUIDANCE - Help user understand and apply information

RESPONSE FORMAT:
📄 DOCUMENT SUMMARY: [Overview of content]
🔍 KEY FINDINGS: [Important information identified]
✅ PROCEDURE ASSESSMENT: [Evaluation of emergency procedures]
💡 RECOMMENDATIONS: [Suggested improvements]
🎯 IMPLEMENTATION STEPS: [How to use this information]

USER MESSAGE (with PDF): {user_message}

Analyze the document and provide expert guidance on disaster management procedures.
""",
            
            "psychological_support": """
CONTEXT: User is experiencing anxiety, stress, trauma, or psychological distress related to disasters or emergency situations.

SUPPORT APPROACH:
1. IMMEDIATE GROUNDING - Provide calming techniques
2. VALIDATION - Acknowledge feelings and normalize responses
3. BREATHING EXERCISES - Guide through calming techniques
4. SAFETY ASSURANCE - Help assess current safety
5. RESOURCE CONNECTION - Suggest professional support if needed

RESPONSE FORMAT:
🫂 EMOTIONAL SUPPORT: [Validation and empathy]
🌬️ IMMEDIATE TECHNIQUES: [Breathing, grounding exercises]
🛡️ SAFETY CHECK: [Current safety assessment]
📞 RESOURCES: [Professional support options if needed]
💪 COPING STRATEGIES: [Long-term resilience building]

USER MESSAGE: {user_message}

Provide compassionate, trauma-informed psychological support focused on disaster-related stress.
""",
            
            "emergency_protocol": """
CONTEXT: User needs immediate emergency guidance or is in an active emergency situation.

PROTOCOL RESPONSE:
1. IMMEDIATE SAFETY - Priority actions for safety
2. EMERGENCY SERVICES - When and how to contact help
3. EVACUATION PROCEDURES - Clear movement instructions
4. COMMUNICATION - How to maintain contact and signal for help
5. SURVIVAL PRIORITIES - Essential needs and resources

RESPONSE FORMAT:
🆘 IMMEDIATE ACTIONS: [Critical first steps]
📞 EMERGENCY CONTACTS: [911, local emergency services]
🏃 EVACUATION STEPS: [Safe movement procedures]
📡 COMMUNICATION: [How to stay connected/signal]
🎒 SURVIVAL NEEDS: [Essential resources and priorities]

EMERGENCY SITUATION: {user_message}

Provide immediate, life-saving emergency response guidance.
"""
        }
        
        self.psychological_keywords = [
            'anxious', 'anxiety', 'scared', 'afraid', 'worried', 'panic', 'stress',
            'overwhelmed', 'helpless', 'trauma', 'ptsd', 'depression', 'fear'
        ]
        
        # Keywords that indicate ACTUAL emergencies (user is in danger)
        self.emergency_keywords = [
            'trapped', 'help me', 'immediate danger', 'urgent help', 'emergency now',
            'evacuation needed', 'injured', 'collapse', 'stuck', 'surrounded',
            'cannot escape', 'need rescue', 'in danger', 'emergency situation'
        ]
        
        # Keywords that indicate information requests (not emergencies)
        self.information_keywords = [
            'news', 'update', 'information', 'status', 'report', 'today',
            'yesterday', 'current', 'latest', 'what happened', 'tell me about',
            'is there', 'any news', 'what is', 'how is', 'condition',
            'situation in', 'about the', 'regarding'
        ]
        
        # Disaster-related keywords that could be either emergency or informational
        self.disaster_keywords = [
            'fire', 'flood', 'earthquake', 'cyclone', 'tsunami', 'landslide',
            'hurricane', 'tornado', 'volcano', 'drought', 'storm'
        ]
    
    def analyze_message_type(self, message: str, has_files: bool = False, file_types: Optional[List[str]] = None) -> str:
        """Determine the appropriate prompt type based on message content and files"""
        message_lower = message.lower()
        
        # Check for files first
        if has_files and file_types:
            if any('image' in ft for ft in file_types):
                return 'image_analysis'
            elif any('video' in ft for ft in file_types):
                return 'video_analysis'
            elif any('pdf' in ft for ft in file_types):
                return 'pdf_analysis'
        
        # Check for psychological support needs
        if any(keyword in message_lower for keyword in self.psychological_keywords):
            return 'psychological_support'
        
        # Check if this is an information request about disasters
        is_information_request = any(keyword in message_lower for keyword in self.information_keywords)
        has_disaster_content = any(keyword in message_lower for keyword in self.disaster_keywords)
        
        # If it's clearly an information request about disasters, use disaster_information prompt
        if is_information_request and has_disaster_content:
            return 'disaster_information'
        
        # Check for emergency situations (user is actually in danger)
        is_emergency = any(keyword in message_lower for keyword in self.emergency_keywords)
        
        # Only trigger emergency protocol if there are clear emergency indicators
        # and it's NOT an information request
        if is_emergency and not is_information_request:
            return 'emergency_protocol'
        
        # Default to text-only analysis
        return 'text_only'
    
    def create_specialized_prompt(self, user_message: str, message_type: str = 'text_only', 
                                 context: Optional[Dict] = None, preferences: Optional[Dict] = None) -> str:
        """Create a specialized prompt based on the message type with enhanced context"""
        template = self.specialized_prompts.get(message_type, self.specialized_prompts['text_only'])
        
        # Add context information to the prompt if available
        context_info = ""
        if context:
            input_method = context.get('inputMethod', 'text')
            session_id = context.get('sessionId', 'unknown')
            previous_context = context.get('previousContext')
            
            context_info += f"\n\nCONTEXT INFORMATION:\n"
            context_info += f"- Input Method: {input_method}\n"
            context_info += f"- Session ID: {session_id}\n"
            
            if previous_context:
                context_info += f"- Previous Messages: {previous_context.get('messageCount', 0)}\n"
                context_info += f"- Chat Topic: {previous_context.get('chatTitle', 'New Chat')}\n"
                if previous_context.get('recentMessages'):
                    context_info += f"- Recent Context:\n{previous_context['recentMessages']}\n"
        
        # Add preferences information
        if preferences:
            context_info += f"\nUSER PREFERENCES:\n"
            for key, value in preferences.items():
                context_info += f"- {key}: {value}\n"
        
        specialized_prompt = self.base_context + context_info + "\n\n" + template.format(user_message=user_message)
        return specialized_prompt

class GeminiAPIHandler:
    """Handles communication with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini API configured successfully")
            except Exception as e:
                logger.error(f"Failed to configure Gemini API: {e}")
                self.model = None
        else:
            if genai is None:
                logger.warning("Google Generative AI not available - install with: pip install google-generativeai")
            else:
                logger.warning("Gemini API key not configured")
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.model is not None
    
    def process_text_request(self, specialized_prompt: str) -> str:
        """Process text-only request with Gemini API"""
        if not self.is_available():
            return "🔴 **Server Status: Gemini API Unavailable**\n\nThe AI service is currently not configured or experiencing issues. This could be due to:\n\n• Missing or invalid API key\n• Network connectivity issues\n• Service temporarily down\n\n💡 **What you can do:**\n• Check your internet connection\n• Verify API key configuration\n• Try again in a few moments\n• Contact support if the issue persists\n\n**Emergency Note:** If you're experiencing an immediate emergency, please call 911 or your local emergency services right away."
        
        try:
            if self.model is None:
                return "🔴 **Server Status: AI Model Unavailable**\n\nThe AI model failed to initialize. This usually indicates:\n\n• Invalid API key configuration\n• Service authentication issues\n• Temporary service disruption\n\n💡 **Recommended actions:**\n• Check API key validity\n• Wait a few minutes and try again\n• Contact technical support\n\n**Emergency Note:** For immediate assistance with disasters or emergencies, please contact local emergency services directly."
            
            response = self.model.generate_content(specialized_prompt)
            
            if not response:
                return "🔴 **Server Status: No Response Received**\n\nThe AI service didn't provide a response. This might be due to:\n\n• Temporary service overload\n• Request processing issues\n• Content filtering restrictions\n\n💡 **Please try:**\n• Rephrasing your question\n• Waiting a moment and trying again\n• Simplifying your request\n\n**Emergency Note:** For urgent situations, contact emergency services immediately."
            
            if not hasattr(response, 'text') or not response.text:
                return "🔴 **Server Status: Invalid Response Format**\n\nReceived an unexpected response format from the AI service. This indicates:\n\n• Service compatibility issues\n• Response parsing problems\n• Temporary service malfunction\n\n💡 **Next steps:**\n• Try your request again\n• Check service status\n• Contact support if problem persists\n\n**Emergency Note:** If this is an emergency, please call 911 or local emergency services."
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API text error: {e}")
            
            # Provide specific error messages based on exception type
            error_msg = str(e).lower()
            
            if 'api_key' in error_msg or 'authentication' in error_msg or 'unauthorized' in error_msg:
                return "🔑 **Server Status: Authentication Failed**\n\nThe AI service authentication failed. This usually means:\n\n• Invalid or expired API key\n• Insufficient permissions\n• Account access issues\n\n💡 **Resolution:**\n• Verify API key is correct and active\n• Check account status\n• Contact administrator for key renewal\n\n**Emergency Note:** For immediate emergency assistance, contact local emergency services directly."
            
            elif 'quota' in error_msg or 'limit' in error_msg or 'exceeded' in error_msg:
                return "📊 **Server Status: Service Quota Exceeded**\n\nThe AI service has reached its usage limits:\n\n• Daily/monthly quota exceeded\n• Rate limiting in effect\n• Resource allocation exhausted\n\n💡 **What to do:**\n• Wait for quota reset (usually next day/month)\n• Contact administrator for quota increase\n• Try again later\n\n**Emergency Note:** If you need immediate emergency assistance, please call 911 or local emergency services."
            
            elif 'network' in error_msg or 'connection' in error_msg or 'timeout' in error_msg:
                return "🌐 **Server Status: Network Connection Issues**\n\nUnable to connect to AI services due to:\n\n• Internet connectivity problems\n• Server network issues\n• Service temporarily unreachable\n\n💡 **Troubleshooting:**\n• Check your internet connection\n• Try again in a few minutes\n• Contact network administrator\n\n**Emergency Note:** For urgent situations requiring immediate help, contact emergency services directly."
            
            elif 'service' in error_msg or 'unavailable' in error_msg or 'down' in error_msg:
                return "⚠️ **Server Status: AI Service Temporarily Down**\n\nThe AI service is currently experiencing issues:\n\n• Service maintenance in progress\n• Temporary server outage\n• System updates being applied\n\n💡 **Expected resolution:**\n• Service should resume shortly\n• Check back in 10-15 minutes\n• Monitor service status page\n\n**Emergency Note:** If this is an emergency situation, do not wait - contact 911 or your local emergency services immediately."
            
            else:
                return f"❌ **Server Status: Unexpected Error**\n\nAn unexpected error occurred while processing your request:\n\n**Error details:** {str(e)[:200]}\n\n💡 **Recommended actions:**\n• Try your request again\n• Simplify your message\n• Contact technical support if issue persists\n\n**Emergency Note:** For immediate emergency assistance, please call 911 or local emergency services directly."
    
    def process_multimodal_request(self, specialized_prompt: str, file_data: bytes, mime_type: str) -> str:
        """Process request with file attachment using Gemini API"""
        if not self.is_available():
            return "🔴 **File Analysis Service Unavailable**\n\nThe AI file analysis service is currently not available due to:\n\n• Missing or invalid API key\n• Service configuration issues\n• Network connectivity problems\n\n💡 **For file analysis, you can:**\n• Describe what you see in the file manually\n• Try uploading again after checking connection\n• Contact support for API key assistance\n\n**Emergency Note:** If your file shows an emergency situation, describe it in text and call 911 if immediate help is needed."
        
        try:
            # Prepare the content parts
            content_parts = [specialized_prompt]
            
            # Add file data based on type
            if mime_type.startswith('image/'):
                # For images, encode as base64 and create proper format
                file_b64 = base64.b64encode(file_data).decode('utf-8')
                image_part = {
                    "mime_type": mime_type,
                    "data": file_b64
                }
                content_parts = [
                    specialized_prompt,
                    image_part
                ]
            
            elif mime_type.startswith('video/'):
                # For videos, encode as base64 and create proper format
                file_b64 = base64.b64encode(file_data).decode('utf-8')
                video_part = {
                    "mime_type": mime_type,
                    "data": file_b64
                }
                content_parts = [
                    specialized_prompt,
                    video_part
                ]
            
            elif mime_type == 'application/pdf':
                # For PDFs, extract text and add as context
                pdf_text = self.extract_pdf_text(file_data)
                content_parts = [specialized_prompt + f"\n\nPDF CONTENT:\n{pdf_text}"]
            
            if self.model is None:
                return "🔴 **File Analysis Model Unavailable**\n\nThe AI model for file analysis failed to initialize:\n\n• Invalid API key configuration\n• Service authentication issues\n• Model loading problems\n\n💡 **Alternative options:**\n• Describe your file content in text\n• Check API key configuration\n• Try again in a few minutes\n\n**Emergency Note:** If your file contains emergency information, please describe the situation in text and contact emergency services if needed."
            
            response = self.model.generate_content(content_parts)
            
            if not response:
                return "🔴 **File Analysis Failed**\n\nNo response received from the file analysis service:\n\n• File might be too large or complex\n• Service temporarily overloaded\n• File format processing issues\n\n💡 **What you can try:**\n• Upload a smaller or different file\n• Describe the file content manually\n• Try again in a few moments\n\n**Emergency Note:** If your file shows an emergency, describe what you see and contact 911 if immediate help is needed."
            
            if not hasattr(response, 'text') or not response.text:
                return "🔴 **File Analysis Response Error**\n\nReceived invalid response from file analysis service:\n\n• Response format issues\n• Content filtering restrictions\n• Processing limitations\n\n💡 **Recommended actions:**\n• Try uploading a different file\n• Describe your file content in text\n• Contact support if problem persists\n\n**Emergency Note:** For urgent situations, describe what you see in the file and contact emergency services directly."
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API multimodal error: {e}")
            
            # Provide specific error messages for file processing
            error_msg = str(e).lower()
            
            if 'file size' in error_msg or 'too large' in error_msg or 'exceeds' in error_msg:
                return "📁 **File Too Large for Analysis**\n\nYour file exceeds the processing limits:\n\n• Maximum file size exceeded\n• Processing capacity limits reached\n• Service resource constraints\n\n💡 **Solutions:**\n• Try a smaller file (under 10MB)\n• Compress the file if possible\n• Describe the file content manually\n\n**Emergency Note:** If your file shows an emergency situation, describe what you see in text and call 911 if immediate help is needed."
            
            elif 'format' in error_msg or 'unsupported' in error_msg or 'invalid' in error_msg:
                return "📄 **Unsupported File Format**\n\nThe file format cannot be processed:\n\n• File type not supported\n• Corrupted file data\n• Invalid file encoding\n\n💡 **Supported formats:**\n• Images: JPG, PNG, GIF\n• Videos: MP4, AVI, MOV\n• Documents: PDF\n\n**Emergency Note:** If your file contains emergency information, please describe the content in text and contact emergency services if needed."
            
            elif 'network' in error_msg or 'connection' in error_msg or 'timeout' in error_msg:
                return "🌐 **File Upload Network Error**\n\nNetwork issues prevented file processing:\n\n• Connection timeout during upload\n• Network connectivity problems\n• Service temporarily unreachable\n\n💡 **Try these steps:**\n• Check your internet connection\n• Try uploading again\n• Use a smaller file if possible\n\n**Emergency Note:** If this file shows an emergency, describe the situation in text and contact 911 immediately if help is needed."
            
            else:
                return f"❌ **File Processing Error**\n\nUnexpected error during file analysis:\n\n**Error details:** {str(e)[:200]}\n\n💡 **Alternative approaches:**\n• Describe your file content in text\n• Try uploading a different file\n• Contact technical support\n\n**Emergency Note:** If your file relates to an emergency situation, describe what you see and contact emergency services immediately if help is needed."
    
    def extract_pdf_text(self, pdf_data: bytes) -> str:
        """Extract text from PDF data"""
        if PyPDF2 is None:
            return "PDF processing not available - install PyPDF2: pip install PyPDF2"
            
        try:
            pdf_file = BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            return "\n".join(text_content)
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return "Error extracting PDF content"

class ChatbotBackend:
    """Main backend service for disaster management chatbot"""
    
    def __init__(self):
        self.prompt_engine = DisasterPromptEngine()
        self.gemini_handler = GeminiAPIHandler()
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'pdf'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_file_size(self, file_data: bytes) -> bool:
        """Validate file size"""
        return len(file_data) <= self.max_file_size
    
    def process_chat_request(self, message: str, files: Optional[List[Dict]] = None, 
                            context: Optional[Dict] = None, preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a chat request with optional files and enhanced context"""
        try:
            # Extract context information
            context = context or {}
            preferences = preferences or {}
            
            input_method = context.get('inputMethod', 'text')
            session_id = context.get('sessionId', 'unknown')
            previous_context = context.get('previousContext')
            
            logger.info(f"Processing message via {input_method} for session {session_id}")
            
            # Determine message type and create specialized prompt
            file_types = [f.get('mime_type', '') for f in (files or [])]
            has_files = bool(files)
            
            message_type = self.prompt_engine.analyze_message_type(
                message, has_files, file_types
            )
            
            # Create specialized prompt with enhanced context
            specialized_prompt = self.prompt_engine.create_specialized_prompt(
                message, message_type, context, preferences
            )
            
            # Process with Gemini API
            if has_files and files:
                # Handle multimodal request
                file_data = files[0]['data']  # Process first file
                mime_type = files[0]['mime_type']
                filename = files[0].get('filename', 'unknown')
                
                logger.info(f"Processing file: {filename} ({mime_type})")
                
                response = self.gemini_handler.process_multimodal_request(
                    specialized_prompt, file_data, mime_type
                )
            else:
                # Handle text-only request
                response = self.gemini_handler.process_text_request(specialized_prompt)
            
            return {
                'success': True,
                'response': response,
                'message_type': message_type,
                'input_method': input_method,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'has_files': has_files,
                'context_used': bool(previous_context)
            }
            
        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': "⚠️ Sorry, I encountered an error processing your request. Please try again.",
                'timestamp': datetime.now().isoformat()
            }

# Initialize backend
chatbot_backend = ChatbotBackend()

# API Routes
@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Main chat endpoint for processing user messages with enhanced context"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '')
            context = data.get('context', {})
            preferences = data.get('preferences', {})
            files_data = data.get('files', [])
        else:
            message = request.form.get('message', '')
            context_str = request.form.get('context', '{}')
            preferences_str = request.form.get('preferences', '{}')
            
            # Parse JSON strings
            try:
                context = json.loads(context_str)
                preferences = json.loads(preferences_str)
            except json.JSONDecodeError:
                context = {}
                preferences = {}
            
            files_data = []
            
            # Handle file uploads
            if 'files' in request.files:
                uploaded_files = request.files.getlist('files')
                for file in uploaded_files:
                    if file and file.filename and chatbot_backend.is_allowed_file(file.filename):
                        file_data = file.read()
                        if chatbot_backend.validate_file_size(file_data):
                            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
                            files_data.append({
                                'data': file_data,
                                'mime_type': mime_type,
                                'filename': secure_filename(file.filename)
                            })
        
        if not message.strip():
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Log incoming request for debugging
        logger.info(f"Processing chat request: {message[:100]}...")
        logger.info(f"Context: {context}")
        logger.info(f"Files: {len(files_data)} files")
        
        # Process the chat request with enhanced context
        result = chatbot_backend.process_chat_request(message, files_data, context, preferences)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'response': "⚠️ Sorry, I encountered an error. Please try again."
        }), 500

@app.route('/api/config', methods=['POST'])
def configure_api():
    """Configure Gemini API key"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key is required'
            }), 400
        
        # Update Gemini handler with new API key
        chatbot_backend.gemini_handler = GeminiAPIHandler(api_key)
        
        return jsonify({
            'success': True,
            'message': 'API key configured successfully',
            'gemini_available': chatbot_backend.gemini_handler.is_available()
        })
        
    except Exception as e:
        logger.error(f"Config endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Configuration failed'
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get backend status and availability"""
    return jsonify({
        'backend_available': True,
        'gemini_available': chatbot_backend.gemini_handler.is_available(),
        'supported_files': list(chatbot_backend.allowed_extensions),
        'max_file_size_mb': chatbot_backend.max_file_size // (1024 * 1024),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 10MB.'
    }), 413

@app.errorhandler(415)
def unsupported_media_type(e):
    return jsonify({
        'success': False,
        'error': 'Unsupported file type.'
    }), 415

if __name__ == '__main__':
    # Configure for development
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Disaster Management Chatbot Backend on port {port}")
    logger.info(f"Gemini API available: {chatbot_backend.gemini_handler.is_available()}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
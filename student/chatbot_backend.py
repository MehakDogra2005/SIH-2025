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

import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import PyPDF2

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
        self.base_context = """You are DisasterAI, an advanced emergency support assistant specialized in disaster management, psychological support, and safety guidance. You provide:

1. IMMEDIATE SAFETY GUIDANCE - Clear, actionable safety instructions
2. PSYCHOLOGICAL SUPPORT - Calming, empathetic responses for anxiety and stress
3. EDUCATIONAL CONTENT - Disaster preparedness and response knowledge
4. EMERGENCY PROTOCOLS - Step-by-step emergency procedures
5. RESOURCE CONNECTIONS - Links to emergency services and support

RESPONSE GUIDELINES:
- Prioritize safety above all else
- Provide clear, actionable steps
- Use calming, supportive language
- Include relevant emergency contacts when appropriate
- Be concise but comprehensive
- Use emojis appropriately for clarity and emotional support
"""
        
        self.specialized_prompts = {
            "text_only": """
CONTEXT: User is seeking disaster-related guidance through text communication.

RESPONSE APPROACH:
- Assess urgency level of the situation
- Provide immediate safety guidance if emergency
- Offer psychological support for anxiety/stress
- Give educational information for preparedness
- Use structured, clear formatting

CURRENT USER MESSAGE:
{user_message}

Please provide a helpful, supportive response focusing on disaster management and safety.
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
        
        self.emergency_keywords = [
            'emergency', 'trapped', 'danger', 'immediate', 'urgent', 'help',
            'evacuation', 'fire', 'flood', 'earthquake', 'collapse', 'injured'
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
        
        # Check for emergency situations
        if any(keyword in message_lower for keyword in self.emergency_keywords):
            return 'emergency_protocol'
        
        # Default to text-only analysis
        return 'text_only'
    
    def create_specialized_prompt(self, user_message: str, message_type: str = 'text_only') -> str:
        """Create a specialized prompt based on the message type"""
        template = self.specialized_prompts.get(message_type, self.specialized_prompts['text_only'])
        specialized_prompt = self.base_context + "\n\n" + template.format(user_message=user_message)
        return specialized_prompt

class GeminiAPIHandler:
    """Handles communication with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Gemini API configured successfully")
            except Exception as e:
                logger.error(f"Failed to configure Gemini API: {e}")
                self.model = None
        else:
            logger.warning("Gemini API key not configured")
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.model is not None
    
    def process_text_request(self, specialized_prompt: str) -> str:
        """Process text-only request with Gemini API"""
        if not self.is_available():
            return "⚠️ Gemini API is not configured. Please provide an API key to use advanced AI features."
        
        try:
            if self.model is None:
                return "⚠️ Gemini model is not available. Please check your API key configuration."
            
            response = self.model.generate_content(specialized_prompt)
            return response.text if response and hasattr(response, 'text') else "⚠️ No response received from Gemini API."
        except Exception as e:
            logger.error(f"Gemini API text error: {e}")
            return f"⚠️ Error processing request: {str(e)}"
    
    def process_multimodal_request(self, specialized_prompt: str, file_data: bytes, mime_type: str) -> str:
        """Process request with file attachment using Gemini API"""
        if not self.is_available():
            return "⚠️ Gemini API is not configured. Please provide an API key to use file analysis features."
        
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
                return "⚠️ Gemini model is not available. Please check your API key configuration."
            
            response = self.model.generate_content(content_parts)
            return response.text if response and hasattr(response, 'text') else "⚠️ No response received from Gemini API."
            
        except Exception as e:
            logger.error(f"Gemini API multimodal error: {e}")
            return f"⚠️ Error processing file: {str(e)}"
    
    def extract_pdf_text(self, pdf_data: bytes) -> str:
        """Extract text from PDF data"""
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
    
    def process_chat_request(self, message: str, files: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Process a chat request with optional files"""
        try:
            # Determine message type and create specialized prompt
            file_types = [f.get('mime_type', '') for f in (files or [])]
            has_files = bool(files)
            
            message_type = self.prompt_engine.analyze_message_type(
                message, has_files, file_types
            )
            
            specialized_prompt = self.prompt_engine.create_specialized_prompt(
                message, message_type
            )
            
            # Process with Gemini API
            if has_files and files:
                # Handle multimodal request
                file_data = files[0]['data']  # Process first file
                mime_type = files[0]['mime_type']
                
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
                'timestamp': datetime.now().isoformat(),
                'has_files': has_files
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
    """Main chat endpoint for processing user messages"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '')
            files_data = data.get('files', [])
        else:
            message = request.form.get('message', '')
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
        
        # Process the chat request
        result = chatbot_backend.process_chat_request(message, files_data)
        
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
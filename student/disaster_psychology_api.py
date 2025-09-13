"""
Flask API for Disaster Psychology SLM Integration
Connects LLAMA-based chatbot with visual assessment module
Provides REST endpoints for emergency psychological support
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import base64
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
import traceback

# Import our custom modules
try:
    from llama_disaster_psychology_trainer import DisasterPsychologySLMTrainer
    from visual_disaster_assessment import VisualDisasterAnalyzer, DisasterAssessment
    from disaster_psychology_training_data import DisasterPsychologyDataGenerator
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

class DisasterPsychologyAPI:
    """Main API class for disaster psychology chatbot"""
    
    def __init__(self):
        """Initialize the API with models and analyzers"""
        self.slm_trainer = None
        self.visual_analyzer = VisualDisasterAnalyzer()
        self.data_generator = DisasterPsychologyDataGenerator()
        self.model_path = None
        self.conversation_history = {}  # Store conversation sessions
        
        # Try to load pre-trained model if available
        self._load_model()
    
    def _load_model(self):
        """Load the trained SLM model if available"""
        try:
            # Look for existing trained model
            model_dirs = [d for d in os.listdir('.') if d.startswith('disaster_psychology_model')]
            if model_dirs:
                self.model_path = sorted(model_dirs)[-1]  # Get latest
                logger.info(f"Found trained model: {self.model_path}")
                self.slm_trainer = DisasterPsychologySLMTrainer()
            else:
                logger.info("No pre-trained model found. Will use fallback responses.")
                self.slm_trainer = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.slm_trainer = None
    
    def generate_fallback_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Generate fallback response when SLM is not available"""
        
        user_input_lower = user_input.lower()
        
        # Emergency situations
        if any(word in user_input_lower for word in ["trapped", "emergency", "help", "stuck"]):
            response = "[EMERGENCY] I understand you're in a critical situation. First, take a deep breath - panic reduces clear thinking. "
            
            if "flood" in user_input_lower or "water" in user_input_lower:
                response += "[EDUCATION] If you're dealing with flood water: Do NOT attempt to walk through moving water. Even 6 inches can knock you down. Stay where you are, move to the highest point available, and signal for help."
            
            elif "fire" in user_input_lower or "smoke" in user_input_lower:
                response += "[EDUCATION] For fire/smoke: Stay low where air is cleaner, feel doors before opening (if hot, don't open), exit immediately if safe path available."
            
            elif "earthquake" in user_input_lower or "building" in user_input_lower:
                response += "[EDUCATION] If building is damaged: Look for cracks, avoid areas with potential falling debris, exit carefully if structure appears compromised."
            
            response += " [CALM] You're being smart by asking for guidance. Contact emergency services (911) with your exact location."
            
        # Panic/anxiety responses
        elif any(word in user_input_lower for word in ["panic", "scared", "afraid", "anxious"]):
            response = "[CALM] I can hear that you're feeling overwhelmed right now, and that's completely understandable. Let's work on calming your mind first. "
            response += "[BREATHING] Try this with me: Breathe in slowly for 4 counts... hold for 4... breathe out for 6 counts. This helps activate your body's calm response. "
            response += "[GROUNDING] Now, name 3 things you can see around you, 2 things you can touch, and 1 sound you can hear. This helps bring you back to the present moment."
            
        # Educational requests
        elif any(word in user_input_lower for word in ["what should", "how to", "what do", "safety"]):
            response = "[EDUCATION] For any emergency situation, follow these priorities: 1) Ensure your immediate safety, 2) Assess the situation calmly, 3) Contact emergency services if needed, 4) Follow evacuation procedures if necessary. "
            response += "For specific disasters: Floods - never walk through moving water; Fires - stay low and exit quickly; Earthquakes - drop, cover, and hold on during shaking."
            
        # General support
        else:
            response = "[CALM] I'm here to help you through this situation. You're not alone, and it's good that you're reaching out for guidance. "
            response += "Can you tell me more about what you're experiencing? Are you in immediate danger, or do you need help with understanding safety procedures?"
        
        return response
    
    def process_text_request(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """Process text-only request for psychological support"""
        
        try:
            # Generate response using SLM or fallback
            if self.slm_trainer and self.model_path:
                response = self.slm_trainer.generate_response(user_input, self.model_path)
            else:
                response = self.generate_fallback_response(user_input)
            
            # Store in conversation history
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            self.conversation_history[session_id].append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "bot_response": response,
                "type": "text_only"
            })
            
            return {
                "success": True,
                "response": response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "response_type": "text_support"
            }
            
        except Exception as e:
            logger.error(f"Error processing text request: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I'm having technical difficulties, but I want you to know that help is available. If this is an emergency, please contact 911 immediately."
            }
    
    def process_image_request(self, image_description: str, user_context: str, session_id: str = "default") -> Dict[str, Any]:
        """Process request with image description for visual assessment"""
        
        try:
            # Analyze image using visual assessment module
            assessment = self.visual_analyzer.analyze_image_description(image_description, user_context)
            
            # Generate comprehensive response
            llm_response = self.visual_analyzer.generate_response_for_llm(assessment, user_context)
            
            # Store in conversation history
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            self.conversation_history[session_id].append({
                "timestamp": datetime.now().isoformat(),
                "user_context": user_context,
                "image_description": image_description,
                "assessment": assessment.__dict__,
                "bot_response": llm_response,
                "type": "visual_assessment"
            })
            
            return {
                "success": True,
                "response": llm_response,
                "assessment": {
                    "disaster_type": assessment.disaster_type,
                    "severity_level": assessment.severity_level,
                    "safety_recommendation": assessment.safety_recommendation,
                    "immediate_actions": assessment.immediate_actions,
                    "confidence_score": assessment.confidence_score
                },
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "response_type": "visual_assessment"
            }
            
        except Exception as e:
            logger.error(f"Error processing image request: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I'm having trouble analyzing the image, but please prioritize your safety. If you're in immediate danger, evacuate to a safe location and contact emergency services."
            }
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        return self.conversation_history.get(session_id, [])
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            return True
        return False

# Initialize API
api = DisasterPsychologyAPI()

# API Routes
@app.route('/')
def home():
    """API documentation and status"""
    return jsonify({
        "service": "Disaster Psychology SLM API",
        "status": "active",
        "endpoints": {
            "POST /chat": "Text-based psychological support",
            "POST /analyze-image": "Visual disaster assessment with photo description",
            "GET /history/<session_id>": "Get conversation history",
            "DELETE /history/<session_id>": "Clear conversation history",
            "GET /health": "API health check",
            "POST /train": "Train model with new data"
        },
        "model_status": "loaded" if api.slm_trainer else "fallback_mode",
        "visual_analyzer": "active"
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": api.slm_trainer is not None,
        "visual_analyzer": "active"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Text-based chat endpoint for psychological support"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'message' in request body"
            }), 400
        
        user_input = data['message']
        session_id = data.get('session_id', 'default')
        
        # Process request
        result = api.process_text_request(user_input, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "fallback_response": "I'm experiencing technical difficulties. If this is an emergency, please contact emergency services immediately."
        }), 500

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Visual disaster assessment endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'image_description' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'image_description' in request body"
            }), 400
        
        image_description = data['image_description']
        user_context = data.get('user_context', '')
        session_id = data.get('session_id', 'default')
        
        # Process visual assessment
        result = api.process_image_request(image_description, user_context, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze-image endpoint: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "fallback_response": "I'm having trouble with image analysis. Please prioritize your safety and contact emergency services if in danger."
        }), 500

@app.route('/history/<session_id>')
def get_history(session_id):
    """Get conversation history for a session"""
    try:
        history = api.get_conversation_history(session_id)
        return jsonify({
            "success": True,
            "session_id": session_id,
            "conversation_count": len(history),
            "history": history
        })
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/history/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    """Clear conversation history for a session"""
    try:
        cleared = api.clear_conversation(session_id)
        return jsonify({
            "success": True,
            "cleared": cleared,
            "session_id": session_id
        })
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/train', methods=['POST'])
def train_model():
    """Train or retrain the model with new data"""
    try:
        data = request.get_json()
        
        # Generate training data
        generator = DisasterPsychologyDataGenerator()
        data_file = "disaster_psychology_training.jsonl"
        generator.save_training_data(data_file)
        
        # Initialize trainer if not available
        if not api.slm_trainer:
            api.slm_trainer = DisasterPsychologySLMTrainer()
        
        # Train model
        model_path = api.slm_trainer.train(data_file)
        api.model_path = model_path
        
        return jsonify({
            "success": True,
            "message": "Model training completed",
            "model_path": model_path,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/test-scenarios', methods=['GET'])
def test_scenarios():
    """Get test scenarios for API testing"""
    scenarios = [
        {
            "type": "text_chat",
            "scenario": "Panic during earthquake",
            "message": "I'm trapped in a college washroom during an earthquake and I'm panicking. The door won't open and I can hear things falling outside. What should I do?"
        },
        {
            "type": "visual_assessment",
            "scenario": "Flood assessment",
            "image_description": "College corridor with knee-deep water, some debris floating, water appears to be moving slowly",
            "user_context": "I'm a student and need to reach the exit to evacuate the building"
        },
        {
            "type": "text_chat",
            "scenario": "Fire emergency support",
            "message": "There's smoke coming under our classroom door and I'm scared. Should we open the door to check what's happening?"
        },
        {
            "type": "visual_assessment",
            "scenario": "Structural damage",
            "image_description": "Large cracks visible in wall after earthquake, some ceiling tiles have fallen",
            "user_context": "We just felt a strong earthquake and I'm not sure if the building is safe"
        }
    ]
    
    return jsonify({
        "success": True,
        "test_scenarios": scenarios,
        "usage": "Use these scenarios to test the /chat and /analyze-image endpoints"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/chat", "/analyze-image", "/history/<session_id>", "/train", "/test-scenarios"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "If this is an emergency, please contact emergency services immediately."
    }), 500

if __name__ == '__main__':
    # Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    
    print(f"""
    Disaster Psychology SLM API Starting...
    =====================================
    
    API Endpoints:
    • POST {HOST}:{PORT}/chat - Text-based psychological support
    • POST {HOST}:{PORT}/analyze-image - Visual disaster assessment  
    • GET {HOST}:{PORT}/history/<session_id> - Get conversation history
    • GET {HOST}:{PORT}/test-scenarios - Get test scenarios
    
    Model Status: {'Loaded' if api.slm_trainer else 'Fallback Mode'}
    Visual Analyzer: Active
    
    Ready to provide emergency psychological support!
    """)
    
    # Start the Flask application
    app.run(host=HOST, port=PORT, debug=DEBUG)
# DisasterCare AI - LLAMA-powered Emergency Psychology Chatbot
## Complete Setup & Usage Guide

### 🚀 Quick Start

This system integrates a LLAMA-based Small Language Model (SLM) with visual disaster assessment for emergency psychological support and educational guidance.

### 📁 Project Structure

```
SIH-2025/
├── consultation.html                       # Main chatbot interface with photo upload
├── disaster_psychology_training_data.py    # Training data generator
├── llama_disaster_psychology_trainer.py    # LLAMA fine-tuning pipeline
├── visual_disaster_assessment.py           # Image analysis module
├── disaster_psychology_api.py              # Flask API server
├── requirements.txt                        # Python dependencies
└── README.md                              # This file
```

### 🛠️ Installation

1. **Install Python Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Optional: Install LLAMA Model** (requires approval):
```bash
# For actual LLAMA models, you'll need:
pip install peft bitsandbytes
# And download model weights from Hugging Face
```

3. **Generate Training Data**:
```bash
python disaster_psychology_training_data.py
```

4. **Train the Model** (optional - uses fallback if not trained):
```bash
python llama_disaster_psychology_trainer.py
```

### ▶️ Running the System

1. **Start the API Server**:
```bash
python disaster_psychology_api.py
```
Server will start on `http://localhost:5000`

2. **Open the Web Interface**:
Open `consultation.html` in your web browser

### 🎯 Key Features

#### 1. **Text-Based Emergency Support**
- LLAMA-powered psychological first aid
- Stress management and panic reduction
- Educational guidance for disasters
- Crisis intervention protocols

#### 2. **Visual Disaster Assessment**
- Upload disaster photos for AI analysis
- Safety recommendations based on visual assessment
- Severity level detection (low/moderate/high/critical)
- Immediate action guidance

#### 3. **Emergency Protocols**
- Flood safety protocols
- Fire evacuation procedures  
- Earthquake response guidelines
- Panic attack management

### 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health check |
| `/chat` | POST | Text-based psychological support |
| `/analyze-image` | POST | Visual disaster assessment |
| `/history/<session_id>` | GET | Get conversation history |
| `/test-scenarios` | GET | Get test scenarios |

### 💬 Usage Examples

#### Text Chat:
```javascript
{
  "message": "I'm trapped in a college washroom during an earthquake and panicking",
  "session_id": "user123"
}
```

#### Photo Analysis:
```javascript
{
  "image_description": "Knee-deep flood water in college corridor with debris",
  "user_context": "I'm a student and need to reach the exit",
  "session_id": "user123"
}
```

### 🧠 AI Response Format

The AI provides structured responses with different types of guidance:

- **🚨 EMERGENCY**: Critical safety information
- **🧠 PSYCHOLOGY**: Psychological support and calming techniques
- **📚 EDUCATION**: Educational guidance and procedures
- **🫁 BREATHING**: Breathing exercises for anxiety
- **⚡ GROUNDING**: Grounding techniques for panic
- **📸 ANALYSIS**: Photo analysis results

### 🔧 Configuration

#### API Configuration (disaster_psychology_api.py):
```python
HOST = '0.0.0.0'        # API host
PORT = 5000             # API port
DEBUG = True            # Debug mode
```

#### Model Configuration:
```python
model_name = "microsoft/DialoGPT-medium"  # Base model
max_length = 512                          # Max sequence length
```

### 🧪 Testing the System

1. **Test API Connection**:
```bash
curl http://localhost:5000/health
```

2. **Test Chat Endpoint**:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need help with panic during flood"}'
```

3. **Get Test Scenarios**:
```bash
curl http://localhost:5000/test-scenarios
```

### 🎨 Web Interface Features

#### Main Chat Interface:
- Real-time messaging with AI
- Typing indicators
- Message formatting with emergency tags
- Session persistence

#### Photo Upload:
- Drag & drop image upload
- Context description input
- Real-time analysis with AI
- Safety recommendations display

#### Emergency Tools:
- Quick access to emergency protocols
- Crisis hotline information
- Professional appointment booking
- Mental health resources

### 🚨 Emergency Integration

The system integrates with emergency services:

- **911**: Immediate danger situations
- **988**: Suicide & Crisis Lifeline
- **741741**: Crisis text line (text "HOME")

### 📊 Training Data

The system includes comprehensive training scenarios:

- **Psychology Support**: Panic attacks, trauma response, anxiety management
- **Educational Guidance**: Earthquake procedures, flood safety, fire evacuation
- **Visual Assessment**: Photo analysis for disasters with depth/severity detection
- **Communication**: Emergency communication and stress de-escalation

### 🔒 Safety & Privacy

- No personal data stored permanently
- Session-based conversation history
- Emergency protocols prioritize immediate safety
- Professional referral system available

### 🛠️ Troubleshooting

#### API Not Connecting:
- Check if Flask server is running on port 5000
- Ensure firewall allows connections
- Verify requirements.txt dependencies installed

#### Model Training Issues:
- System falls back to rule-based responses if model unavailable
- Check GPU memory for large model training
- Reduce batch size if encountering memory errors

#### Photo Upload Problems:
- Ensure image files are under 5MB
- Check browser JavaScript console for errors
- Verify file types are supported (JPG, PNG, GIF)

### 🚀 Deployment

For production deployment:

1. **Use production WSGI server**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 disaster_psychology_api:app
```

2. **Configure reverse proxy** (nginx/Apache)
3. **Set up SSL certificates** for HTTPS
4. **Configure proper logging** and monitoring

### 📈 Performance Optimization

- **Model Quantization**: Use 8-bit/16-bit models for faster inference
- **Caching**: Implement Redis for session caching
- **CDN**: Use CDN for static assets
- **Load Balancing**: Multiple API instances for high traffic

### 🤝 Contributing

To extend the system:

1. **Add New Disaster Types**: Update `disaster_patterns` in visual analyzer
2. **Improve Training Data**: Add scenarios to training data generator
3. **Enhance UI**: Modify consultation.html for new features
4. **Add Languages**: Implement multi-language support

### 📞 Support

For emergency situations:
- **Immediate Danger**: Call 911
- **Mental Health Crisis**: Call 988
- **Text Crisis Support**: Text HOME to 741741

### 📝 License

This project is developed for the Smart India Hackathon 2025 - Disaster Education Platform.

---

**Note**: This is an AI-powered system designed to complement, not replace, professional emergency services and mental health care. Always contact appropriate emergency services for immediate danger situations.
"""
Disaster Psychology SLM Training Data Generator
Creates comprehensive training datasets for fine-tuning LLAMA model on:
1. Emergency psychological support and crisis intervention
2. Educational disaster response guidance
3. Real-time scenario-based assistance
"""

import json
import random
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TrainingExample:
    """Structure for training examples"""
    user_input: str
    context: str
    psychology_response: str
    education_response: str
    emergency_level: str  # low, medium, high, critical
    disaster_type: str
    
class DisasterPsychologyDataGenerator:
    """Generate training data for disaster psychology SLM"""
    
    def __init__(self):
        self.disaster_types = [
            "earthquake", "flood", "fire", "cyclone", "landslide", 
            "tsunami", "tornado", "avalanche", "volcanic_eruption", "pandemic"
        ]
        
        self.emergency_scenarios = {
            "trapped_indoor": ["locked in washroom", "trapped in elevator", "stuck in building", "classroom lockdown"],
            "outdoor_exposure": ["open ground during earthquake", "flood water rising", "fire approaching", "debris falling"],
            "communication_need": ["need teacher help", "emergency contact", "family notification", "medical assistance"],
            "psychological_state": ["panic attack", "extreme fear", "confusion", "trauma response", "shock"]
        }
        
        self.psychology_techniques = {
            "breathing": "Take slow, deep breaths. Inhale for 4 counts, hold for 4, exhale for 6. This activates your parasympathetic nervous system.",
            "grounding": "Use the 5-4-3-2-1 technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "reassurance": "You are not alone. Help is on the way. You're doing the right thing by reaching out.",
            "focus": "Focus on what you can control right now. One step at a time. You're capable of handling this.",
            "safety_first": "Your safety is the priority. Stay calm, assess your immediate surroundings, and follow safety protocols."
        }
        
        self.educational_responses = {
            "earthquake": {
                "indoor": "DROP, COVER, HOLD ON. Get under a sturdy desk/table. Protect your head. Stay away from windows.",
                "outdoor": "Move away from buildings, trees, power lines. Drop to ground, protect head. Wait for shaking to stop.",
                "after": "Check for injuries. Look for hazards. If trapped, tap on pipes/walls to signal rescuers."
            },
            "flood": {
                "rising_water": "Move to higher ground immediately. Avoid walking in moving water. 6 inches can knock you down.",
                "trapped": "If water is rising, go to highest floor. Signal for help. Don't enter flood water - it may be contaminated.",
                "evacuation": "Take emergency kit. Turn off utilities. Follow evacuation routes. Don't drive through flooded roads."
            },
            "fire": {
                "escape": "Stay low - crawl under smoke. Feel doors before opening. If clothes catch fire: STOP, DROP, ROLL.",
                "trapped": "Close doors, seal cracks with cloth. Signal from window. Call for help. Don't open doors to smoke.",
                "smoke": "Get out fast. Smoke is more dangerous than flames. If trapped, go to room with window, signal for help."
            }
        }
    
    def generate_psychology_training_data(self) -> List[Dict[str, Any]]:
        """Generate training data focused on psychological support"""
        training_data = []
        
        # Panic and anxiety scenarios
        panic_scenarios = [
            {
                "user_input": "I'm trapped in the college washroom during an earthquake. The door is jammed and I'm having a panic attack. I can't breathe properly and I'm shaking.",
                "context": "Student trapped during earthquake, experiencing panic attack, needs immediate psychological support",
                "psychology_response": "I understand you're scared - that's completely normal. First, let's focus on your breathing. Take a slow, deep breath in through your nose for 4 counts... hold it for 4... now breathe out slowly through your mouth for 6 counts. You're safe right now. The shaking has stopped. You're going to be okay. Let's do this breathing together 3 more times.",
                "education_response": "After we calm your breathing, check if the door handle turns or if the door frame is warped. Try pushing firmly on different parts of the door. If it won't open, bang on the pipes or shout 'HELP' every few minutes to conserve energy. The building emergency team will be doing room-by-room checks.",
                "emergency_level": "high",
                "disaster_type": "earthquake"
            },
            {
                "user_input": "Flood water is entering our college building. I'm on the second floor but water is rising fast. I'm terrified and don't know what to do. My friends are panicking too.",
                "context": "Group of students on second floor during flood, rising water, group panic situation",
                "psychology_response": "Take a deep breath. You're on the second floor - that's good. You have time and you're not in immediate danger. Your fear is protecting you - it's making you alert. Now, I need you to be the calm leader for your friends. Speak in a steady voice, tell them 'We're safe on this floor, we have a plan.' Your calmness will help them too.",
                "education_response": "Move to the highest point of the building immediately. Gather emergency supplies if available (water, food, flashlights). Signal for help from windows using bright cloth or phone flashlight. Don't attempt to wade through flood water. Send your location to emergency services: text your exact building and floor number to local emergency contact.",
                "emergency_level": "critical",
                "disaster_type": "flood"
            }
        ]
        
        # Educational guidance scenarios
        educational_scenarios = [
            {
                "user_input": "Earthquake started while I'm in the college cafeteria. Should I run outside? There are tables around me and other students are running.",
                "context": "Student in cafeteria during earthquake, needs immediate action guidance",
                "psychology_response": "I know your instinct is to run, but stay calm. You're going to be okay. Don't follow the crowd running - that's actually more dangerous. Take a deep breath and follow the steps I'm about to give you.",
                "education_response": "DO NOT RUN OUTSIDE during shaking! Drop immediately, get under the nearest sturdy table, cover your head and neck with your arms. Hold on to the table and be prepared to move with it. Most injuries happen when people try to run during shaking. After shaking stops completely, then walk calmly to the designated evacuation area.",
                "emergency_level": "high",
                "disaster_type": "earthquake"
            },
            {
                "user_input": "Fire alarm went off in our college building. I can smell smoke but I'm on the 4th floor. Elevator or stairs?",
                "context": "Student on 4th floor during fire emergency, needs evacuation guidance",
                "psychology_response": "You're being smart by asking rather than panicking. You can handle this situation. Stay focused on the steps, move with purpose but don't rush in a way that could cause you to fall.",
                "education_response": "NEVER use elevators during fire - they can trap you or take you to the fire floor. Use stairs only. Before opening any door, feel it with the back of your hand - if it's hot, don't open. If cool, open slowly. Stay low if there's smoke - crawl if needed. Keep one hand on the wall to guide you. Count floors as you go down.",
                "emergency_level": "high",
                "disaster_type": "fire"
            }
        ]
        
        # Photo analysis scenarios
        photo_analysis_scenarios = [
            {
                "user_input": "I'm sending you a photo of flood water in our college corridor. How deep do you think it is? Is it safe to walk through?",
                "context": "Student requesting visual assessment of flood water depth for safety decision",
                "psychology_response": "Thank you for being cautious and asking before acting - that shows good judgment under pressure. Let me help you assess this safely.",
                "education_response": "From the photo, I can see the water is knee-deep and moving. This is NOT safe to walk through. Even 6 inches of moving water can knock you down. Stay where you are. If you must move, use a sturdy stick to test depth ahead of each step. Look for submerged obstacles. Water may be contaminated with sewage or chemicals. Signal for rescue instead.",
                "emergency_level": "critical",
                "disaster_type": "flood"
            }
        ]
        
        training_data.extend(panic_scenarios)
        training_data.extend(educational_scenarios)
        training_data.extend(photo_analysis_scenarios)
        
        return training_data
    
    def generate_stress_management_data(self) -> List[Dict[str, Any]]:
        """Generate training data for stress and trauma management"""
        stress_scenarios = [
            {
                "user_input": "I survived the earthquake but I keep shaking and can't stop thinking about it. Every small vibration makes me panic. Is this normal?",
                "context": "Post-disaster trauma response, hypervigilance, need for normalization and coping strategies",
                "psychology_response": "What you're experiencing is completely normal and shows that your mind and body are processing a traumatic event. This is called hypervigilance - your nervous system is trying to protect you. You're not broken, you're having a normal response to an abnormal situation. These feelings will decrease over time with proper support.",
                "education_response": "Practice grounding techniques: Plant your feet firmly on the ground, name 5 things you can see, 4 you can touch, 3 you can hear. This helps your nervous system understand you're safe now. Gentle movement like walking can help process the stress hormones. Consider reaching out to a counselor - professional support can significantly help recovery.",
                "emergency_level": "medium",
                "disaster_type": "earthquake"
            },
            {
                "user_input": "My friend is not responding after we were rescued from the flood. She's just staring and won't talk. What should I do?",
                "context": "Friend showing signs of acute stress reaction or shock, need for immediate psychological first aid",
                "psychology_response": "Your friend is likely in shock - a natural protective response to trauma. Stay calm and be her anchor right now. Sit near her, speak in a gentle, steady voice. Let her know she's safe and that you're there with her. Don't pressure her to talk, but keep providing gentle reassurance.",
                "education_response": "Keep her warm and comfortable. Ensure she's in a safe, quiet space. Speak slowly and clearly: 'You're safe now. The flood is over. I'm here with you.' Don't leave her alone. Watch for signs of injury she might not be aware of. Get medical attention - shock can mask serious injuries. Professional help is important even if she seems physically okay.",
                "emergency_level": "high",
                "disaster_type": "flood"
            }
        ]
        
        return stress_scenarios
    
    def generate_communication_training_data(self) -> List[Dict[str, Any]]:
        """Generate training data for emergency communication scenarios"""
        communication_scenarios = [
            {
                "user_input": "I need to contact my teacher for help but my phone has no signal. We're trapped on the 3rd floor after the landslide. How do I get help?",
                "context": "Students trapped, need to establish communication with authorities, limited connectivity",
                "psychology_response": "You're being resourceful by trying to establish communication - that's excellent problem-solving under stress. Stay calm, we'll find a way to get help to you.",
                "education_response": "Try these communication methods in order: 1) Move to different areas to find signal, especially near windows. 2) Send SMS instead of calls - they use less signal. 3) Use any available WiFi to send messages through social media or messaging apps. 4) Create noise: bang on pipes, walls, or windows in a pattern (3 short, 3 long, 3 short - SOS). 5) Use a flashlight or phone light to signal from windows.",
                "emergency_level": "critical",
                "disaster_type": "landslide"
            },
            {
                "user_input": "I'm using the disaster management app to alert teachers but I don't know how to explain where exactly we are in the building. It's urgent.",
                "context": "Student using emergency app, needs guidance on providing precise location information",
                "psychology_response": "You're doing exactly the right thing by using the emergency app. Take a moment to gather the specific details - this information will help rescuers find you quickly.",
                "education_response": "Provide these details in your message: 1) Building name and address, 2) Floor number, 3) Room number or area (like 'east side corridor'), 4) Number of people with you, 5) Any injuries, 6) Your name and contact info, 7) Landmark details like 'near the blue exit sign' or 'classroom with broken window'. Take a photo of any room numbers or signs if possible.",
                "emergency_level": "high",
                "disaster_type": "general"
            }
        ]
        
        return communication_scenarios
    
    def generate_multi_scenario_dataset(self) -> List[Dict[str, Any]]:
        """Generate comprehensive training dataset"""
        all_training_data = []
        
        # Generate psychology-focused data
        all_training_data.extend(self.generate_psychology_training_data())
        
        # Generate stress management data
        all_training_data.extend(self.generate_stress_management_data())
        
        # Generate communication data
        all_training_data.extend(self.generate_communication_training_data())
        
        # Add variations for different disaster types
        base_scenarios = all_training_data.copy()
        for scenario in base_scenarios:
            for disaster_type in ["earthquake", "flood", "fire", "cyclone"]:
                if scenario["disaster_type"] != disaster_type:
                    # Create variations for different disaster types
                    adapted_scenario = self._adapt_scenario_for_disaster(scenario, disaster_type)
                    if adapted_scenario:
                        all_training_data.append(adapted_scenario)
        
        return all_training_data
    
    def _adapt_scenario_for_disaster(self, base_scenario: Dict[str, Any], new_disaster_type: str) -> Dict[str, Any]:
        """Adapt a scenario for a different disaster type"""
        adaptations = {
            "earthquake": {
                "keywords": ["earthquake", "shaking", "tremor", "seismic"],
                "specific_advice": "Drop, Cover, Hold On protocol"
            },
            "flood": {
                "keywords": ["flood", "water", "rising", "drowning"],
                "specific_advice": "Move to higher ground, avoid moving water"
            },
            "fire": {
                "keywords": ["fire", "smoke", "burning", "heat"],
                "specific_advice": "Stay low, crawl under smoke, feel doors"
            },
            "cyclone": {
                "keywords": ["cyclone", "wind", "storm", "debris"],
                "specific_advice": "Stay away from windows, find interior room"
            }
        }
        
        # Simple adaptation logic - in a real implementation, this would be more sophisticated
        if new_disaster_type in adaptations:
            adapted = base_scenario.copy()
            adapted["disaster_type"] = new_disaster_type
            # More sophisticated adaptation would modify the text content
            return adapted
        
        return None
    
    def save_training_data(self, filename: str = "disaster_psychology_training.jsonl"):
        """Save training data in JSONL format for model training"""
        training_data = self.generate_multi_scenario_dataset()
        
        with open(filename, 'w', encoding='utf-8') as f:
            for example in training_data:
                # Format for LLAMA fine-tuning
                formatted_example = {
                    "instruction": f"You are a disaster psychology support chatbot. User situation: {example['context']}",
                    "input": example["user_input"],
                    "output": f"PSYCHOLOGICAL SUPPORT: {example['psychology_response']}\n\nEDUCATIONAL GUIDANCE: {example['education_response']}\n\nEMERGENCY LEVEL: {example['emergency_level'].upper()}",
                    "disaster_type": example["disaster_type"],
                    "emergency_level": example["emergency_level"]
                }
                f.write(json.dumps(formatted_example, ensure_ascii=False) + '\n')
        
        print(f"Training data saved to {filename}")
        print(f"Total examples: {len(training_data)}")
        
        # Generate statistics
        disaster_counts = {}
        emergency_counts = {}
        for example in training_data:
            disaster_counts[example["disaster_type"]] = disaster_counts.get(example["disaster_type"], 0) + 1
            emergency_counts[example["emergency_level"]] = emergency_counts.get(example["emergency_level"], 0) + 1
        
        print("\nDataset Statistics:")
        print("Disaster Types:", disaster_counts)
        print("Emergency Levels:", emergency_counts)
        
        return training_data

# Example usage and testing
if __name__ == "__main__":
    generator = DisasterPsychologyDataGenerator()
    
    print("Generating Disaster Psychology Training Dataset...")
    print("=" * 60)
    
    # Generate and save training data
    training_data = generator.save_training_data()
    
    # Show sample examples
    print("\nSample Training Examples:")
    print("-" * 40)
    
    for i, example in enumerate(training_data[:3]):
        print(f"\nExample {i+1}:")
        print(f"Disaster Type: {example['disaster_type']}")
        print(f"Emergency Level: {example['emergency_level']}")
        print(f"User Input: {example['user_input'][:100]}...")
        print(f"Psychology Response: {example['psychology_response'][:100]}...")
        print(f"Education Response: {example['education_response'][:100]}...")
        print("-" * 40)
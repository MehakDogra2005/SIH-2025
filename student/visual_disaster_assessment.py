"""
Visual Disaster Assessment Module
Analyzes disaster photos/images and provides psychological support + educational guidance
Integrates with LLAMA-based disaster psychology chatbot
"""

import base64
from typing import Dict, List, Any, Tuple
import json
import re
from datetime import datetime
from dataclasses import dataclass

@dataclass
class DisasterAssessment:
    """Results of visual disaster assessment"""
    disaster_type: str
    severity_level: str  # low, moderate, high, critical
    safety_recommendation: str
    psychological_support: str
    educational_guidance: str
    immediate_actions: List[str]
    photo_analysis: Dict[str, Any]
    confidence_score: float

class VisualDisasterAnalyzer:
    """Analyze disaster images and provide comprehensive guidance"""
    
    def __init__(self):
        """Initialize the visual analyzer"""
        self.disaster_patterns = {
            "flood": {
                "keywords": ["water", "flooding", "submerged", "current", "debris", "muddy"],
                "depth_indicators": ["ankle", "knee", "waist", "chest", "ceiling"],
                "danger_signs": ["moving water", "debris", "electrical", "contamination"]
            },
            "fire": {
                "keywords": ["smoke", "flames", "fire", "burning", "ash", "charred"],
                "severity_indicators": ["light smoke", "heavy smoke", "visible flames", "intense fire"],
                "danger_signs": ["blocked exits", "structural damage", "toxic smoke"]
            },
            "earthquake": {
                "keywords": ["cracks", "collapsed", "rubble", "tilted", "broken"],
                "damage_indicators": ["minor cracks", "major cracks", "partial collapse", "total collapse"],
                "danger_signs": ["unstable structure", "falling debris", "broken gas lines"]
            },
            "structural": {
                "keywords": ["collapsed", "damaged", "broken", "cracked", "unsafe"],
                "stability_indicators": ["stable", "compromised", "unstable", "collapsed"],
                "danger_signs": ["falling objects", "structural failure", "blocked exits"]
            }
        }
        
        self.psychology_responses = {
            "panic": {
                "immediate": "[CALM] I can see this is overwhelming. Let's take this step by step. You're safe right now, and we'll figure out the best course of action together.",
                "breathing": "[BREATHING] Take a slow, deep breath with me. In for 4 counts... hold for 4... out for 6. This will help clear your thinking.",
                "grounding": "[GROUNDING] Name 3 things you can see around you, 2 things you can touch, and 1 thing you can hear. This helps you stay present."
            },
            "fear": {
                "validation": "[CALM] Your fear is completely normal in this situation. It shows you're being smart and cautious about safety.",
                "empowerment": "You're already doing the right thing by assessing the situation before acting. That's excellent judgment.",
                "support": "I'm here to help you through this. We'll take it one step at a time."
            },
            "confusion": {
                "clarity": "I understand this situation is confusing. Let me help break down what I see and what options you have.",
                "guidance": "It's normal to feel uncertain in emergencies. We'll focus on the most important safety steps first.",
                "reassurance": "You don't have to figure this out alone. Together we can identify the safest path forward."
            }
        }
        
        self.educational_protocols = {
            "flood_safety": {
                "depth_assessment": {
                    "ankle_deep": "Generally walkable with caution. Wear sturdy shoes, test each step, avoid moving water.",
                    "knee_deep": "DANGEROUS: Do not attempt to walk. 6 inches of moving water can knock down an adult.",
                    "waist_deep": "CRITICAL: Evacuation required. Signal for rescue. Do not enter water."
                },
                "water_quality": "Flood water often contains sewage, chemicals, and debris. Avoid contact with skin and eyes.",
                "electrical_hazards": "Never enter flooded areas with electrical equipment. Assume all water near electrical sources is dangerous.",
                "evacuation_routes": "Identify highest accessible point. Signal for help using phone flashlight, mirror, or loud noises."
            },
            "fire_safety": {
                "smoke_assessment": {
                    "light_smoke": "Stay low, exit quickly. Smoke rises, cleaner air is near the floor.",
                    "heavy_smoke": "Crawl on hands and knees. Cover nose and mouth. Exit immediately.",
                    "blocked_visibility": "Feel your way along walls. Check doors for heat before opening."
                },
                "door_protocol": "Feel door and handle with back of hand. If hot, don't open. Seal gaps with wet cloth.",
                "evacuation_priority": "Exit building immediately. Don't stop for belongings. Meet at designated assembly point.",
                "trapped_procedures": "Signal from windows. Seal room if possible. Call emergency services with exact location."
            },
            "earthquake_response": {
                "during_shaking": {
                    "indoors": "DROP to hands/knees, COVER head/neck, HOLD ON to sturdy furniture.",
                    "outdoors": "Move away from buildings, trees, power lines. Drop and cover.",
                    "trapped": "Stay calm, conserve energy, signal for help, protect airways from dust."
                },
                "after_shaking": "Check for injuries, hazards. Be prepared for aftershocks. Exit if building is damaged.",
                "structural_assessment": "Look for cracks, tilted walls, broken glass. If in doubt, evacuate carefully."
            }
        }
    
    def analyze_image_description(self, description: str, user_context: str = "") -> DisasterAssessment:
        """Analyze image based on text description and user context"""
        
        # Detect disaster type
        disaster_type = self._detect_disaster_type(description)
        
        # Assess severity
        severity_level = self._assess_severity(description, disaster_type)
        
        # Generate psychological support
        psychological_support = self._generate_psychological_support(description, user_context)
        
        # Generate educational guidance
        educational_guidance = self._generate_educational_guidance(disaster_type, description, severity_level)
        
        # Create safety recommendations
        safety_recommendation = self._create_safety_recommendation(disaster_type, severity_level, description)
        
        # Generate immediate actions
        immediate_actions = self._generate_immediate_actions(disaster_type, severity_level, description)
        
        # Photo analysis details
        photo_analysis = self._analyze_photo_details(description, disaster_type)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(description, disaster_type)
        
        return DisasterAssessment(
            disaster_type=disaster_type,
            severity_level=severity_level,
            safety_recommendation=safety_recommendation,
            psychological_support=psychological_support,
            educational_guidance=educational_guidance,
            immediate_actions=immediate_actions,
            photo_analysis=photo_analysis,
            confidence_score=confidence_score
        )
    
    def _detect_disaster_type(self, description: str) -> str:
        """Detect the type of disaster from description"""
        description_lower = description.lower()
        
        for disaster_type, patterns in self.disaster_patterns.items():
            keyword_matches = sum(1 for keyword in patterns["keywords"] if keyword in description_lower)
            if keyword_matches >= 2:  # Require at least 2 matching keywords
                return disaster_type
        
        # Default fallback
        if any(water_word in description_lower for water_word in ["water", "flood", "wet", "submerged"]):
            return "flood"
        elif any(fire_word in description_lower for fire_word in ["smoke", "fire", "burn", "flame"]):
            return "fire"
        elif any(structure_word in description_lower for structure_word in ["crack", "collapse", "damage", "broken"]):
            return "structural"
        else:
            return "general_emergency"
    
    def _assess_severity(self, description: str, disaster_type: str) -> str:
        """Assess severity level based on description and disaster type"""
        description_lower = description.lower()
        
        # Critical indicators
        critical_signs = ["trapped", "can't escape", "rising rapidly", "heavy smoke", "collapse", "critical"]
        if any(sign in description_lower for sign in critical_signs):
            return "critical"
        
        # High severity indicators
        high_signs = ["knee deep", "waist deep", "blocked exit", "spreading", "unstable", "dangerous"]
        if any(sign in description_lower for sign in high_signs):
            return "high"
        
        # Moderate severity indicators
        moderate_signs = ["ankle deep", "light smoke", "minor crack", "manageable", "slow"]
        if any(sign in description_lower for sign in moderate_signs):
            return "moderate"
        
        return "low"
    
    def _generate_psychological_support(self, description: str, user_context: str) -> str:
        """Generate psychological support based on situation"""
        description_lower = description.lower()
        context_lower = user_context.lower()
        
        # Detect emotional state
        if any(panic_word in (description_lower + context_lower) for panic_word in ["panic", "scared", "terrified", "afraid"]):
            return self.psychology_responses["panic"]["immediate"] + " " + self.psychology_responses["panic"]["breathing"]
        
        elif any(fear_word in (description_lower + context_lower) for fear_word in ["worried", "anxious", "nervous", "uncertain"]):
            return self.psychology_responses["fear"]["validation"] + " " + self.psychology_responses["fear"]["empowerment"]
        
        elif any(confusion_word in (description_lower + context_lower) for confusion_word in ["confused", "don't know", "not sure", "unclear"]):
            return self.psychology_responses["confusion"]["clarity"] + " " + self.psychology_responses["confusion"]["guidance"]
        
        else:
            return "[CALM] You're handling this situation well by carefully assessing before acting. That shows excellent judgment and self-control."
    
    def _generate_educational_guidance(self, disaster_type: str, description: str, severity_level: str) -> str:
        """Generate educational guidance based on disaster type and severity"""
        
        if disaster_type == "flood":
            return self._flood_educational_guidance(description, severity_level)
        elif disaster_type == "fire":
            return self._fire_educational_guidance(description, severity_level)
        elif disaster_type == "earthquake" or disaster_type == "structural":
            return self._earthquake_educational_guidance(description, severity_level)
        else:
            return "[EDUCATION] General emergency protocol: 1) Assess immediate dangers, 2) Secure your safety first, 3) Contact emergency services, 4) Follow evacuation procedures if necessary."
    
    def _flood_educational_guidance(self, description: str, severity_level: str) -> str:
        """Specific guidance for flood situations"""
        guidance = "[EDUCATION] FLOOD SAFETY: "
        
        if "knee" in description.lower() or severity_level in ["high", "critical"]:
            guidance += "Water at knee level or higher is EXTREMELY DANGEROUS. Just 6 inches of moving water can knock down an adult. DO NOT attempt to walk through this water. "
            guidance += "ACTIONS: 1) Stay where you are, 2) Move to highest available point, 3) Signal for help using phone light or noise, 4) Wait for rescue personnel."
        
        elif "ankle" in description.lower() or severity_level == "moderate":
            guidance += "Ankle-deep water requires extreme caution. ONLY proceed if: 1) Water is not moving, 2) You have sturdy shoes, 3) You can test each step carefully, 4) You have something to hold onto for balance."
        
        else:
            guidance += "Assess water depth and movement before any action. Even shallow moving water is dangerous."
        
        guidance += " [CRITICAL] All flood water may contain sewage, chemicals, and dangerous debris. Avoid skin contact when possible."
        
        return guidance
    
    def _fire_educational_guidance(self, description: str, severity_level: str) -> str:
        """Specific guidance for fire situations"""
        guidance = "[EDUCATION] FIRE SAFETY: "
        
        if "smoke" in description.lower():
            if severity_level in ["high", "critical"]:
                guidance += "Heavy smoke is IMMEDIATELY LIFE-THREATENING. ACTIONS: 1) Get as low as possible (crawl if necessary), 2) Exit building immediately, 3) Do NOT open doors with smoke coming underneath, 4) If trapped, seal room and signal from windows."
            else:
                guidance += "ANY visible smoke requires immediate evacuation. Stay low where air is cleaner, cover nose/mouth, exit quickly."
        
        guidance += " [CRITICAL] NEVER re-enter a building after evacuation. Meet at designated assembly point away from structure."
        
        return guidance
    
    def _earthquake_educational_guidance(self, description: str, severity_level: str) -> str:
        """Specific guidance for earthquake/structural damage"""
        guidance = "[EDUCATION] EARTHQUAKE/STRUCTURAL SAFETY: "
        
        if "crack" in description.lower() or "damage" in description.lower():
            if severity_level in ["high", "critical"]:
                guidance += "Visible structural damage indicates building is UNSAFE. EVACUATE IMMEDIATELY but carefully. Watch for falling debris, broken glass, and unstable structures."
            else:
                guidance += "Any structural cracks require professional assessment. Exit carefully and do not re-enter until building is inspected."
        
        guidance += " [CRITICAL] Be prepared for aftershocks. If trapped, conserve energy, protect airways from dust, and signal for help periodically."
        
        return guidance
    
    def _create_safety_recommendation(self, disaster_type: str, severity_level: str, description: str) -> str:
        """Create overall safety recommendation"""
        
        if severity_level == "critical":
            return "IMMEDIATE EVACUATION REQUIRED - This situation poses imminent danger to life. Do not delay."
        elif severity_level == "high":
            return "HIGH RISK - Evacuate area safely but quickly. Avoid unnecessary exposure to hazards."
        elif severity_level == "moderate":
            return "PROCEED WITH EXTREME CAUTION - Assess each action carefully and be prepared to retreat."
        else:
            return "LOW RISK - Monitor situation and be prepared to escalate response if conditions worsen."
    
    def _generate_immediate_actions(self, disaster_type: str, severity_level: str, description: str) -> List[str]:
        """Generate list of immediate actions to take"""
        
        actions = []
        
        # Universal actions
        actions.append("Ensure your immediate personal safety")
        actions.append("Contact emergency services if not already done")
        
        # Disaster-specific actions
        if disaster_type == "flood":
            if severity_level in ["high", "critical"]:
                actions.extend([
                    "Do NOT enter or attempt to cross flood water",
                    "Move to highest available location",
                    "Signal for rescue using phone light or noise",
                    "Wait for professional rescue personnel"
                ])
            else:
                actions.extend([
                    "Test water depth and movement carefully",
                    "Ensure you have sturdy footwear",
                    "Identify safe exit route before proceeding"
                ])
        
        elif disaster_type == "fire":
            actions.extend([
                "Exit building immediately if safe to do so",
                "Stay low to avoid smoke inhalation",
                "Feel doors for heat before opening",
                "If trapped, seal room and signal from windows"
            ])
        
        elif disaster_type in ["earthquake", "structural"]:
            actions.extend([
                "Check for immediate hazards (gas leaks, electrical)",
                "Exit building carefully if structural damage visible",
                "Be prepared for aftershocks",
                "Avoid areas with potential falling debris"
            ])
        
        return actions
    
    def _analyze_photo_details(self, description: str, disaster_type: str) -> Dict[str, Any]:
        """Analyze specific details from photo description"""
        
        analysis = {
            "disaster_type": disaster_type,
            "key_observations": [],
            "hazard_indicators": [],
            "escape_route_assessment": "unknown",
            "environmental_factors": []
        }
        
        description_lower = description.lower()
        
        # Extract key observations
        if disaster_type == "flood":
            for depth in ["ankle", "knee", "waist", "chest"]:
                if depth in description_lower:
                    analysis["key_observations"].append(f"Water level: {depth}-deep")
            
            if any(word in description_lower for word in ["moving", "current", "flowing"]):
                analysis["hazard_indicators"].append("Moving water detected")
            
            if any(word in description_lower for word in ["debris", "objects", "furniture"]):
                analysis["hazard_indicators"].append("Debris in water")
        
        elif disaster_type == "fire":
            if any(word in description_lower for word in ["thick", "heavy", "dense"]) and "smoke" in description_lower:
                analysis["hazard_indicators"].append("Heavy smoke concentration")
            
            if "exit" in description_lower or "door" in description_lower:
                if any(word in description_lower for word in ["blocked", "smoke", "hot"]):
                    analysis["escape_route_assessment"] = "compromised"
                else:
                    analysis["escape_route_assessment"] = "potentially_clear"
        
        # Environmental factors
        if any(word in description_lower for word in ["dark", "night", "low visibility"]):
            analysis["environmental_factors"].append("Low visibility conditions")
        
        if any(word in description_lower for word in ["cold", "hot", "weather"]):
            analysis["environmental_factors"].append("Weather considerations needed")
        
        return analysis
    
    def _calculate_confidence(self, description: str, disaster_type: str) -> float:
        """Calculate confidence score for the assessment"""
        
        # Base confidence
        confidence = 0.5
        
        # Increase confidence based on description detail
        word_count = len(description.split())
        if word_count > 20:
            confidence += 0.2
        elif word_count > 10:
            confidence += 0.1
        
        # Increase confidence based on specific indicators
        description_lower = description.lower()
        patterns = self.disaster_patterns.get(disaster_type, {}).get("keywords", [])
        
        keyword_matches = sum(1 for keyword in patterns if keyword in description_lower)
        confidence += min(keyword_matches * 0.1, 0.3)
        
        # Cap at 0.95 (never 100% certain from description alone)
        return min(confidence, 0.95)
    
    def create_assessment_training_data(self) -> List[Dict[str, Any]]:
        """Generate training data for visual assessment scenarios"""
        
        training_scenarios = [
            {
                "image_description": "College corridor with knee-deep muddy water, students visible in background, water appears to be moving slowly, debris floating including papers and a plastic chair",
                "user_context": "I'm a student trapped in college during flood, need to reach the exit",
                "assessment": {
                    "disaster_type": "flood",
                    "severity_level": "high",
                    "safety_recommendation": "HIGH RISK - Do not attempt to walk through knee-deep water",
                    "psychological_support": "[CALM] I can see this is a frightening situation, but you're being smart by assessing before acting. Take a deep breath - we'll figure out the safest approach together.",
                    "educational_guidance": "[EDUCATION] FLOOD SAFETY: Water at knee level is EXTREMELY DANGEROUS. Just 6 inches of moving water can knock down an adult. DO NOT attempt to walk through this water. ACTIONS: 1) Stay where you are, 2) Move to highest available point, 3) Signal for help using phone light, 4) Wait for rescue personnel.",
                    "immediate_actions": [
                        "Do NOT enter the flood water",
                        "Move to highest floor/room available",
                        "Signal for rescue using phone flashlight",
                        "Contact emergency services with exact location"
                    ]
                }
            },
            {
                "image_description": "Classroom with light smoke visible near ceiling, door closed, some students near windows, emergency lighting on",
                "user_context": "Fire alarm went off, we're in classroom, smoke coming under door",
                "assessment": {
                    "disaster_type": "fire",
                    "severity_level": "high",
                    "safety_recommendation": "HIGH RISK - Do not open door with smoke underneath",
                    "psychological_support": "[CALM] You're doing exactly the right thing by not opening the door immediately. Stay calm and follow these safety steps carefully.",
                    "educational_guidance": "[EDUCATION] FIRE SAFETY: NEVER open a door with smoke coming underneath. Feel the door handle with the back of your hand - if it's hot, don't open. Seal the bottom of the door with wet cloth if available. Signal from windows and call emergency services with your exact location.",
                    "immediate_actions": [
                        "Do NOT open the door",
                        "Feel door handle for heat (use back of hand)",
                        "Seal door gaps with wet cloth if available",
                        "Signal from windows for rescue",
                        "Call emergency services immediately"
                    ]
                }
            }
        ]
        
        return training_scenarios
    
    def generate_response_for_llm(self, assessment: DisasterAssessment, user_input: str) -> str:
        """Generate complete response for integration with LLAMA model"""
        
        response_parts = [
            f"[PHOTO_ANALYSIS] I can see this is a {assessment.disaster_type} situation with {assessment.severity_level} severity level.",
            "",
            assessment.psychological_support,
            "",
            assessment.educational_guidance,
            "",
            f"[EMERGENCY] {assessment.safety_recommendation}",
            "",
            "[IMMEDIATE_ACTIONS]"
        ]
        
        for i, action in enumerate(assessment.immediate_actions, 1):
            response_parts.append(f"{i}. {action}")
        
        response_parts.extend([
            "",
            f"[CONFIDENCE] Assessment confidence: {assessment.confidence_score:.0%}",
            "",
            "Stay safe, and remember - you're not alone in this situation. Help is available."
        ])
        
        return "\n".join(response_parts)

# Integration with LLAMA training pipeline
def create_visual_assessment_training_data() -> List[Dict[str, str]]:
    """Create training data for visual assessment integration with LLAMA"""
    
    analyzer = VisualDisasterAnalyzer()
    visual_scenarios = analyzer.create_assessment_training_data()
    
    training_data = []
    
    for scenario in visual_scenarios:
        # Create assessment
        assessment = analyzer.analyze_image_description(
            scenario["image_description"], 
            scenario["user_context"]
        )
        
        # Generate LLAMA training example
        user_input = f"I'm sending you a photo description: {scenario['image_description']}. Context: {scenario['user_context']}. Can you help me with what to do?"
        
        llm_response = analyzer.generate_response_for_llm(assessment, user_input)
        
        training_example = {
            "instruction": "You are an emergency response AI that provides psychological support and educational guidance for disaster situations. Analyze the photo description and provide comprehensive help.",
            "input": user_input,
            "output": llm_response
        }
        
        training_data.append(training_example)
    
    return training_data

# Test the visual analyzer
if __name__ == "__main__":
    analyzer = VisualDisasterAnalyzer()
    
    # Test scenarios
    test_scenarios = [
        {
            "description": "Knee-deep flood water in college corridor with debris floating",
            "context": "I'm a student and need to reach the exit"
        },
        {
            "description": "Heavy smoke visible under classroom door, students by windows",
            "context": "Fire alarm went off, we're trapped in classroom"
        },
        {
            "description": "Large cracks in wall after earthquake, ceiling partially collapsed",
            "context": "Just felt strong earthquake, not sure if building is safe"
        }
    ]
    
    print("Visual Disaster Assessment Test Results")
    print("=" * 50)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\nTest {i}:")
        print(f"Description: {scenario['description']}")
        print(f"Context: {scenario['context']}")
        print("-" * 30)
        
        assessment = analyzer.analyze_image_description(
            scenario["description"], 
            scenario["context"]
        )
        
        response = analyzer.generate_response_for_llm(assessment, scenario['context'])
        print(response)
        print("=" * 50)
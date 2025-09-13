"""
LLAMA-based SLM Fine-tuning Pipeline for Disaster Psychology Chatbot
Handles fine-tuning LLAMA model on disaster psychology and educational guidance data
"""

import torch
import transformers
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset, load_dataset
import json
from typing import Dict, List, Any
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DisasterPsychologySLMTrainer:
    """Fine-tune LLAMA model for disaster psychology support"""
    
    def __init__(self, 
                 model_name: str = "microsoft/DialoGPT-medium",  # Alternative: "meta-llama/Llama-2-7b-chat-hf"
                 max_length: int = 512,
                 device: str = "auto"):
        """
        Initialize the trainer
        
        Args:
            model_name: Base model to fine-tune (LLAMA or alternative)
            max_length: Maximum sequence length
            device: Device to use for training
        """
        self.model_name = model_name
        self.max_length = max_length
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load tokenizer and model
        self.tokenizer = None
        self.model = None
        self.setup_model()
        
    def setup_model(self):
        """Initialize model and tokenizer"""
        try:
            logger.info(f"Loading tokenizer for {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Add special tokens for disaster psychology
            special_tokens = {
                "additional_special_tokens": [
                    "[PSYCHOLOGY]", "[EDUCATION]", "[EMERGENCY]", "[CALM]", 
                    "[CRITICAL]", "[PHOTO_ANALYSIS]", "[BREATHING]", "[GROUNDING]"
                ]
            }
            self.tokenizer.add_special_tokens(special_tokens)
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info(f"Loading model {self.model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            # Resize embeddings to account for new tokens
            self.model.resize_token_embeddings(len(self.tokenizer))
            
            logger.info("Model and tokenizer loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to a smaller model
            logger.info("Falling back to GPT-2 medium")
            self.model_name = "gpt2-medium"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
    def load_training_data(self, data_path: str) -> Dataset:
        """Load and preprocess training data"""
        logger.info(f"Loading training data from {data_path}")
        
        # Load JSONL data
        training_examples = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                example = json.loads(line.strip())
                training_examples.append(example)
        
        logger.info(f"Loaded {len(training_examples)} training examples")
        
        # Convert to format suitable for causal language modeling
        formatted_data = []
        for example in training_examples:
            # Create input-output format
            input_text = f"[EMERGENCY] User: {example['input']}\nAssistant: {example['output']}"
            formatted_data.append({"text": input_text})
        
        # Create dataset
        dataset = Dataset.from_list(formatted_data)
        return dataset
    
    def tokenize_data(self, dataset: Dataset) -> Dataset:
        """Tokenize the dataset"""
        def tokenize_function(examples):
            tokenized = self.tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=self.max_length,
                return_tensors="pt"
            )
            # For causal LM, labels are the same as input_ids
            tokenized["labels"] = tokenized["input_ids"].clone()
            return tokenized
        
        logger.info("Tokenizing dataset...")
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset
    
    def setup_training_args(self, output_dir: str = "./disaster_psychology_model") -> TrainingArguments:
        """Setup training arguments"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"{output_dir}_{timestamp}"
        
        return TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=2,  # Small batch size for memory efficiency
            per_device_eval_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=100,
            max_steps=1000,  # Limit steps for quick training
            logging_steps=50,
            save_steps=200,
            eval_steps=200,
            evaluation_strategy="steps",
            learning_rate=5e-5,
            weight_decay=0.01,
            fp16=True if self.device == "cuda" else False,
            push_to_hub=False,
            report_to=None,  # Disable wandb/tensorboard for simplicity
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        )
    
    def train(self, data_path: str, output_dir: str = "./disaster_psychology_model"):
        """Main training function"""
        logger.info("Starting disaster psychology SLM training...")
        
        # Load and preprocess data
        dataset = self.load_training_data(data_path)
        tokenized_dataset = self.tokenize_data(dataset)
        
        # Split dataset
        train_size = int(0.9 * len(tokenized_dataset))
        train_dataset = tokenized_dataset.select(range(train_size))
        eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))
        
        # Setup training arguments
        training_args = self.setup_training_args(output_dir)
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # We're doing causal LM, not masked LM
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Train the model
        logger.info("Starting training...")
        trainer.train()
        
        # Save the final model
        logger.info(f"Saving model to {training_args.output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(training_args.output_dir)
        
        logger.info("Training completed!")
        return training_args.output_dir
    
    def generate_response(self, user_input: str, model_path: str = None) -> str:
        """Generate response using the trained model"""
        if model_path:
            # Load trained model
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Format input
        prompt = f"[EMERGENCY] User: {user_input}\nAssistant:"
        
        # Tokenize input
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + 200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        if "Assistant:" in response:
            assistant_response = response.split("Assistant:")[-1].strip()
            return assistant_response
        
        return response

class DisasterPhotoAnalyzer:
    """Analyze disaster photos and provide safety recommendations"""
    
    def __init__(self):
        self.safety_guidelines = {
            "flood": {
                "ankle_deep": "CAUTION: Proceed slowly with sturdy shoes. Test each step.",
                "knee_deep": "DANGER: Do not attempt to walk. Moving water can knock you down.",
                "waist_deep": "CRITICAL: Evacuation required. Signal for rescue immediately.",
                "contaminated": "WARNING: Water may contain sewage, chemicals, or debris."
            },
            "fire": {
                "visible_flames": "EVACUATE: Leave immediately via safest route.",
                "heavy_smoke": "DANGER: Stay low, crawl if necessary. Exit immediately.",
                "blocked_exit": "ALERT: Signal from window. Don't open doors to smoke."
            },
            "structural": {
                "cracks": "CAUTION: Building integrity compromised. Evacuate carefully.",
                "collapsed_ceiling": "DANGER: More collapse likely. Exit immediately.",
                "broken_glass": "HAZARD: Wear shoes, clear safe path slowly."
            }
        }
    
    def analyze_flood_photo(self, image_description: str) -> Dict[str, str]:
        """Analyze flood photo and provide recommendations"""
        # This would integrate with actual image analysis AI
        # For now, we'll simulate based on description
        
        recommendations = {
            "safety_level": "high_risk",
            "immediate_action": "Do not attempt to walk through this water",
            "psychology_support": "I can see this is a frightening situation. You're being smart by checking before acting.",
            "next_steps": "Stay where you are, signal for help, wait for rescue",
            "technical_details": "Water appears knee-deep with visible current - too dangerous for walking"
        }
        
        return recommendations
    
    def create_photo_analysis_training_data(self) -> List[Dict[str, Any]]:
        """Create training data for photo analysis scenarios"""
        photo_scenarios = [
            {
                "user_input": "I'm sending a photo of flood water in our building corridor. It looks like it's up to my knees. Can I walk through it to reach the exit?",
                "context": "Student requesting safety assessment of knee-deep flood water",
                "psychology_response": "[CALM] I understand you want to reach safety, and it's smart that you're asking before acting. Take a deep breath - we'll figure out the safest approach together.",
                "education_response": "[EDUCATION] From your description, knee-deep water is extremely dangerous to walk through. Even 6 inches of moving water can knock down an adult. [EMERGENCY] Stay where you are. Look for: 1) Any higher ground nearby, 2) Sturdy objects to hold onto, 3) Alternative routes. Signal for help using phone flashlight or noise.",
                "emergency_level": "critical",
                "disaster_type": "flood"
            },
            {
                "user_input": "Photo shows smoke coming under our classroom door. The hallway looks dark with smoke. Should we open the door to check?",
                "context": "Students in classroom with smoke in hallway, decision about opening door",
                "psychology_response": "[CALM] You're doing exactly the right thing by checking first instead of just opening the door. Stay calm and follow these steps carefully.",
                "education_response": "[EDUCATION] NEVER open a door with smoke coming under it. [EMERGENCY] Feel the door handle and door itself with the back of your hand. If it's hot, don't open. Seal the bottom of the door with wet cloth if available. Signal from windows. Call emergency services with your exact location.",
                "emergency_level": "critical",
                "disaster_type": "fire"
            }
        ]
        
        return photo_scenarios

# Training execution script
def main():
    """Main execution function"""
    logger.info("Disaster Psychology SLM Training Pipeline")
    logger.info("=" * 50)
    
    # Initialize trainer
    trainer = DisasterPsychologySLMTrainer()
    
    # Check if training data exists
    data_file = "disaster_psychology_training.jsonl"
    if not os.path.exists(data_file):
        logger.info("Training data not found. Generating...")
        from disaster_psychology_training_data import DisasterPsychologyDataGenerator
        
        generator = DisasterPsychologyDataGenerator()
        generator.save_training_data(data_file)
    
    # Train the model
    model_path = trainer.train(data_file)
    
    # Test the trained model
    logger.info("Testing trained model...")
    test_inputs = [
        "I'm trapped in a college washroom during an earthquake and I'm panicking. What should I do?",
        "Flood water is rising in our building. I'm scared and don't know if it's safe to walk through.",
        "I can see smoke in the hallway. Should I open the door to check what's happening?"
    ]
    
    for test_input in test_inputs:
        response = trainer.generate_response(test_input, model_path)
        logger.info(f"\nInput: {test_input}")
        logger.info(f"Response: {response}")
        logger.info("-" * 50)
    
    logger.info(f"Model training complete! Saved to: {model_path}")

if __name__ == "__main__":
    main()
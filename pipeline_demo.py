#!/usr/bin/env python3
"""
Complete Requirements Engineering Pipeline Demo
==============================================

This script demonstrates the complete pipeline for requirements engineering:
1. Audio transcription using Whisper
2. Requirements field extraction using Flan-T5
3. Text preprocessing using spaCy
4. Combined output with structured results

Requirements:
- All dependencies from requirements.txt installed
- Audio file named 'sample.wav' in the same directory
- FFmpeg installed on system
"""

import whisper
import spacy
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class RequirementsPipeline:
    """
    Complete pipeline for requirements engineering using pre-trained models.
    """
    
    def __init__(self):
        """Initialize the pipeline with all required models."""
        self.whisper_model = None
        self.spacy_model = None
        self.flan_tokenizer = None
        self.flan_model = None
        
    def load_models(self):
        """Load all required models."""
        print("Loading all models...")
        print("=" * 50)
        
        # Load Whisper model
        print("1. Loading Whisper model...")
        self.whisper_model = whisper.load_model("small")
        print("   [OK] Whisper model loaded")
        
        # Load spaCy model
        print("2. Loading spaCy model...")
        try:
            self.spacy_model = spacy.load("en_core_web_sm")
            print("   [OK] spaCy model loaded")
        except OSError:
            print("   [ERROR] spaCy model not found. Please run: python -m spacy download en_core_web_sm")
            return False
        
        # Load Flan-T5 model
        print("3. Loading Flan-T5 model...")
        self.flan_tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        self.flan_model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
        print("   [OK] Flan-T5 model loaded")
        
        print("\nAll models loaded successfully!")
        return True
    
    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_file_path (str): Path to audio file
        
        Returns:
            str: Transcribed text
        """
        print(f"\nTranscribing audio: {audio_file_path}")
        print("-" * 30)
        
        result = self.whisper_model.transcribe(audio_file_path)
        transcribed_text = result["text"]
        
        print(f"Transcription completed!")
        print(f"Text: {transcribed_text}")
        
        return transcribed_text
    
    def extract_requirements_fields(self, text):
        """
        Extract structured requirements fields using Flan-T5.
        
        Args:
            text (str): Input text
        
        Returns:
            dict: Extracted fields
        """
        print(f"\nExtracting requirements fields...")
        print("-" * 30)
        
        # Create prompt for requirements extraction
        prompt = f"""
Extract the following requirements fields from this text:

Text: {text}

Please extract and format the following fields:
1. Purpose: What is the main purpose or goal?
2. Scope: What is the scope or boundaries?
3. Product Functions: What are the main functions or features?
4. Constraints: What are the limitations or constraints?
5. Stakeholders: Who are the main stakeholders or users?

Format your response as:
Purpose: [extracted purpose]
Scope: [extracted scope]
Product Functions: [extracted functions]
Constraints: [extracted constraints]
Stakeholders: [extracted stakeholders]
"""
        
        # Tokenize and generate
        inputs = self.flan_tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
        
        with torch.no_grad():
            outputs = self.flan_model.generate(
                inputs,
                max_length=512,
                num_beams=4,
                early_stopping=True,
                temperature=0.7,
                do_sample=True
            )
        
        # Decode the output
        generated_text = self.flan_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse the extracted fields
        fields = self._parse_extracted_fields(generated_text)
        
        print("Requirements extraction completed!")
        for key, value in fields.items():
            print(f"  {key}: {value}")
        
        return fields
    
    def preprocess_text(self, text):
        """
        Preprocess text using spaCy.
        
        Args:
            text (str): Input text
        
        Returns:
            dict: Preprocessing results
        """
        print(f"\nPreprocessing text with spaCy...")
        print("-" * 30)
        
        doc = self.spacy_model(text)
        
        # Extract key information
        sentences = [sent.text.strip() for sent in doc.sents]
        
        # Identify ambiguous words
        ambiguous_words = []
        ambiguous_patterns = [
            'should', 'could', 'might', 'may', 'can', 'will', 'shall',
            'often', 'sometimes', 'usually', 'typically', 'generally',
            'fast', 'slow', 'large', 'small', 'many', 'few', 'several',
            'easy', 'difficult', 'simple', 'complex', 'user-friendly',
            'efficient', 'effective', 'reliable', 'secure', 'stable'
        ]
        
        for token in doc:
            if token.text.lower() in ambiguous_patterns:
                start = max(0, token.i - 2)
                end = min(len(doc), token.i + 3)
                context = doc[start:end].text
                
                ambiguous_words.append({
                    'word': token.text,
                    'context': context,
                    'reason': 'Potentially ambiguous word'
                })
        
        # Extract entities and noun phrases
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        
        preprocessing_results = {
            'sentences': sentences,
            'ambiguous_words': ambiguous_words,
            'entities': entities,
            'noun_phrases': noun_phrases
        }
        
        print("Text preprocessing completed!")
        print(f"  Sentences: {len(sentences)}")
        print(f"  Ambiguous words: {len(ambiguous_words)}")
        print(f"  Entities: {len(entities)}")
        print(f"  Noun phrases: {len(noun_phrases)}")
        
        return preprocessing_results
    
    def _parse_extracted_fields(self, extracted_text):
        """Parse extracted text into structured fields."""
        fields = {}
        lines = extracted_text.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                fields[key] = value
        
        return fields
    
    def run_complete_pipeline(self, audio_file_path):
        """
        Run the complete requirements engineering pipeline.
        
        Args:
            audio_file_path (str): Path to audio file
        
        Returns:
            dict: Complete pipeline results
        """
        print("Requirements Engineering Pipeline")
        print("=" * 50)
        print(f"Processing audio file: {audio_file_path}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Transcribe audio
        transcribed_text = self.transcribe_audio(audio_file_path)
        
        # Step 2: Extract requirements fields
        extracted_fields = self.extract_requirements_fields(transcribed_text)
        
        # Step 3: Preprocess text
        preprocessing_results = self.preprocess_text(transcribed_text)
        
        # Combine all results
        complete_results = {
            'timestamp': datetime.now().isoformat(),
            'audio_file': audio_file_path,
            'transcribed_text': transcribed_text,
            'extracted_fields': extracted_fields,
            'preprocessing_results': preprocessing_results
        }
        
        return complete_results
    
    def save_results(self, results, output_file="pipeline_results.json"):
        """Save pipeline results to JSON file."""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nComplete results saved to: {output_file}")

def main():
    """Main function to run the complete pipeline."""
    # Check if sample audio file exists
    audio_file = "sample.wav"
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found!")
        print("Please place a sample audio file named 'sample.wav' in this directory.")
        print("\nYou can:")
        print("1. Record a short audio clip and save it as 'sample.wav'")
        print("2. Download a sample audio file from the internet")
        print("3. Convert an existing audio file to WAV format")
        sys.exit(1)
    
    try:
        # Initialize pipeline
        pipeline = RequirementsPipeline()
        
        # Load all models
        if not pipeline.load_models():
            print("Failed to load models. Please check the error messages above.")
            sys.exit(1)
        
        # Run complete pipeline
        results = pipeline.run_complete_pipeline(audio_file)
        
        # Display summary
        print(f"\nPipeline Summary:")
        print("=" * 50)
        print(f"Audio file: {results['audio_file']}")
        print(f"Transcribed text: {results['transcribed_text'][:100]}...")
        print(f"Extracted fields: {len(results['extracted_fields'])}")
        print(f"Sentences: {len(results['preprocessing_results']['sentences'])}")
        print(f"Ambiguous words: {len(results['preprocessing_results']['ambiguous_words'])}")
        
        # Save results
        pipeline.save_results(results)
        
        print(f"\nPipeline completed successfully!")
        
    except Exception as e:
        print(f"Error during pipeline execution: {str(e)}")
        print("\nCommon issues:")
        print("1. Make sure all dependencies are installed")
        print("2. Check that FFmpeg is installed")
        print("3. Ensure spaCy English model is downloaded")
        print("4. Verify audio file format is supported")
        sys.exit(1)

if __name__ == "__main__":
    main()

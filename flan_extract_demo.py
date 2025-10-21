#!/usr/bin/env python3
"""
Flan-T5 Extraction Demo Script
==============================

This script demonstrates how to use Google's Flan-T5 model to extract structured
requirements fields from text. It uses the "google/flan-t5-base" model to extract
key information like Purpose, Scope, Product Functions, and Constraints.

Requirements:
- Transformers library installed
- Internet connection for first-time model download
"""

from transformers import T5Tokenizer, T5ForConditionalGeneration
import json
import torch
import sys

def load_flan_t5_model(model_name="google/flan-t5-base"):
    """
    Load the Flan-T5 model and tokenizer.
    
    Args:
        model_name (str): Name of the Flan-T5 model to use
    
    Returns:
        tuple: (tokenizer, model)
    """
    print(f"Loading Flan-T5 model: {model_name}")
    print("Note: First run will download the model (~1GB)")
    
    # Load tokenizer and model
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    print("Model loaded successfully!")
    return tokenizer, model

def extract_requirements_fields(text, tokenizer, model):
    """
    Extract structured requirements fields from text using Flan-T5.
    
    Args:
        text (str): Input text to extract fields from
        tokenizer: Flan-T5 tokenizer
        model: Flan-T5 model
    
    Returns:
        dict: Extracted fields
    """
    # Define the prompt for requirements extraction
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
    
    print("Extracting requirements fields...")
    
    # Tokenize the input
    inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
    
    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=512,
            num_beams=4,
            early_stopping=True,
            temperature=0.7,
            do_sample=True
        )
    
    # Decode the output
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print("Extraction completed!")
    return generated_text

def parse_extracted_fields(extracted_text):
    """
    Parse the extracted text into structured fields.
    
    Args:
        extracted_text (str): Raw extracted text from model
    
    Returns:
        dict: Parsed fields
    """
    fields = {}
    lines = extracted_text.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            fields[key] = value
    
    return fields

def main():
    """
    Main function to run the Flan-T5 extraction demo.
    """
    # Sample text for demonstration
    sample_text = """
    We need to develop a mobile application for managing personal finances. 
    The app should allow users to track their income and expenses, create budgets, 
    and generate financial reports. The target users are individuals who want to 
    better manage their personal finances. The app must work on both iOS and Android 
    platforms and should be able to sync data across devices. The development 
    should be completed within 6 months and the budget is limited to $50,000.
    """
    
    print("Flan-T5 Requirements Extraction Demo")
    print("=" * 50)
    print(f"Sample text:\n{sample_text}")
    print("=" * 50)
    
    try:
        # Load the model
        tokenizer, model = load_flan_t5_model()
        
        # Extract fields
        extracted_text = extract_requirements_fields(sample_text, tokenizer, model)
        
        print(f"\nRaw extracted text:\n{'-' * 30}")
        print(extracted_text)
        print(f"{'-' * 30}")
        
        # Parse into structured format
        parsed_fields = parse_extracted_fields(extracted_text)
        
        print(f"\nStructured output:\n{'-' * 30}")
        for key, value in parsed_fields.items():
            print(f"{key}: {value}")
        print(f"{'-' * 30}")
        
        # Save to JSON file
        output_file = "extracted_requirements.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(parsed_fields, f, indent=2, ensure_ascii=False)
        
        print(f"\nStructured output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        print("\nCommon issues:")
        print("1. Make sure you have internet connection for model download")
        print("2. Check that transformers library is properly installed")
        print("3. Ensure you have enough disk space for the model")
        sys.exit(1)

if __name__ == "__main__":
    main()

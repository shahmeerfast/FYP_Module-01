#!/usr/bin/env python3
"""
spaCy Preprocessing Demo Script
==============================

This script demonstrates how to use spaCy for text preprocessing in requirements engineering.
It performs sentence segmentation, tokenization, and identifies potentially ambiguous words
that might need clarification in requirements documents.

Requirements:
- spaCy library installed
- English language model: python -m spacy download en_core_web_sm
"""

import spacy
import re
from collections import Counter

def load_spacy_model(model_name="en_core_web_sm"):
    """
    Load the spaCy English model.
    
    Args:
        model_name (str): Name of the spaCy model to use
    
    Returns:
        spacy.Language: Loaded spaCy model
    """
    try:
        print(f"Loading spaCy model: {model_name}")
        nlp = spacy.load(model_name)
        print("Model loaded successfully!")
        return nlp
    except OSError:
        print(f"Error: Model '{model_name}' not found!")
        print("Please install the English model by running:")
        print(f"python -m spacy download {model_name}")
        return None

def preprocess_text(text, nlp):
    """
    Preprocess text using spaCy for requirements analysis.
    
    Args:
        text (str): Input text to preprocess
        nlp: spaCy language model
    
    Returns:
        dict: Preprocessing results
    """
    print("Processing text with spaCy...")
    
    # Process the text
    doc = nlp(text)
    
    # Extract sentences
    sentences = [sent.text.strip() for sent in doc.sents]
    
    # Extract tokens (words)
    tokens = [token.text for token in doc if not token.is_space and not token.is_punct]
    
    # Extract lemmatized tokens
    lemmas = [token.lemma_ for token in doc if not token.is_space and not token.is_punct]
    
    # Identify potentially ambiguous words
    ambiguous_words = identify_ambiguous_words(doc)
    
    # Extract named entities
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Extract noun phrases
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    
    results = {
        'sentences': sentences,
        'tokens': tokens,
        'lemmas': lemmas,
        'ambiguous_words': ambiguous_words,
        'entities': entities,
        'noun_phrases': noun_phrases,
        'word_frequency': Counter(tokens)
    }
    
    print("Text processing completed!")
    return results

def identify_ambiguous_words(doc):
    """
    Identify potentially ambiguous words in requirements text.
    
    Args:
        doc: spaCy processed document
    
    Returns:
        list: List of ambiguous words with their contexts
    """
    # Words that are commonly ambiguous in requirements
    ambiguous_patterns = [
        'should', 'could', 'might', 'may', 'can', 'will', 'shall',
        'often', 'sometimes', 'usually', 'typically', 'generally',
        'fast', 'slow', 'large', 'small', 'many', 'few', 'several',
        'easy', 'difficult', 'simple', 'complex', 'user-friendly',
        'efficient', 'effective', 'reliable', 'secure', 'stable'
    ]
    
    ambiguous_words = []
    
    for token in doc:
        if token.text.lower() in ambiguous_patterns:
            # Get context around the word
            start = max(0, token.i - 2)
            end = min(len(doc), token.i + 3)
            context = doc[start:end].text
            
            ambiguous_words.append({
                'word': token.text,
                'context': context,
                'position': token.i,
                'reason': 'Commonly ambiguous word in requirements'
            })
    
    return ambiguous_words

def highlight_ambiguous_words(text, ambiguous_words):
    """
    Highlight ambiguous words in the original text.
    
    Args:
        text (str): Original text
        ambiguous_words (list): List of ambiguous words
    
    Returns:
        str: Text with highlighted ambiguous words
    """
    highlighted_text = text
    
    for word_info in ambiguous_words:
        word = word_info['word']
        # Use ** for highlighting in console output
        highlighted_text = highlighted_text.replace(word, f"**{word}**")
    
    return highlighted_text

def main():
    """
    Main function to run the spaCy preprocessing demo.
    """
    # Sample requirements text
    sample_text = """
    The system should provide fast response times for user queries. 
    Users should be able to easily navigate through the interface. 
    The application must be secure and reliable. Data should be 
    backed up regularly. The system should support many concurrent users.
    """
    
    print("spaCy Text Preprocessing Demo")
    print("=" * 50)
    print(f"Sample text:\n{sample_text}")
    print("=" * 50)
    
    # Load spaCy model
    nlp = load_spacy_model()
    if nlp is None:
        return
    
    try:
        # Preprocess the text
        results = preprocess_text(sample_text, nlp)
        
        # Display results
        print(f"\nPreprocessing Results:")
        print(f"{'-' * 30}")
        
        print(f"\n1. Sentences ({len(results['sentences'])}):")
        for i, sentence in enumerate(results['sentences'], 1):
            print(f"   {i}. {sentence}")
        
        print(f"\n2. Tokens ({len(results['tokens'])}):")
        print(f"   {results['tokens'][:10]}...")  # Show first 10 tokens
        
        print(f"\n3. Ambiguous Words ({len(results['ambiguous_words'])}):")
        for word_info in results['ambiguous_words']:
            print(f"   - '{word_info['word']}' in context: '{word_info['context']}'")
        
        print(f"\n4. Named Entities ({len(results['entities'])}):")
        for entity, label in results['entities']:
            print(f"   - {entity} ({label})")
        
        print(f"\n5. Noun Phrases ({len(results['noun_phrases'])}):")
        for phrase in results['noun_phrases'][:5]:  # Show first 5
            print(f"   - {phrase}")
        
        print(f"\n6. Most Common Words:")
        for word, count in results['word_frequency'].most_common(5):
            print(f"   - {word}: {count}")
        
        # Highlight ambiguous words in original text
        highlighted_text = highlight_ambiguous_words(sample_text, results['ambiguous_words'])
        print(f"\n7. Text with Ambiguous Words Highlighted:")
        print(f"   {highlighted_text}")
        
        # Save results to file
        output_file = "preprocessing_results.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("spaCy Preprocessing Results\n")
            f.write("=" * 30 + "\n\n")
            
            f.write("Sentences:\n")
            for i, sentence in enumerate(results['sentences'], 1):
                f.write(f"{i}. {sentence}\n")
            
            f.write(f"\nAmbiguous Words:\n")
            for word_info in results['ambiguous_words']:
                f.write(f"- {word_info['word']}: {word_info['reason']}\n")
                f.write(f"  Context: {word_info['context']}\n")
            
            f.write(f"\nNamed Entities:\n")
            for entity, label in results['entities']:
                f.write(f"- {entity} ({label})\n")
        
        print(f"\nDetailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")
        print("\nCommon issues:")
        print("1. Make sure spaCy is properly installed")
        print("2. Ensure the English model is downloaded")
        print("3. Check that the text is not empty")
        sys.exit(1)

if __name__ == "__main__":
    main()

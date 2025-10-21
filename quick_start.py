#!/usr/bin/env python3
"""
Quick Start Script for Large Scale Requirements Engineering System
================================================================

This script provides a simple way to test and demonstrate the system
with minimal setup required.
"""

import os
import sys
import json
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'torch', 'transformers', 'whisper', 'spacy', 
        'pandas', 'numpy', 'librosa', 'soundfile'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("All dependencies are installed!")
    return True

def check_spacy_model():
    """Check if spaCy English model is installed"""
    print("\nChecking spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("  ✅ en_core_web_sm model is available")
        return True
    except OSError:
        print("  ❌ en_core_web_sm model is missing")
        print("  Please install it using: python -m spacy download en_core_web_sm")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("\nCreating sample data...")
    
    # Create directories
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)
    
    # Create sample requirements files
    sample_requirements = [
        "The stock prediction system must provide real-time price updates for all major stock exchanges including NYSE, NASDAQ, and LSE. The system should update prices every second during market hours.",
        "Users should be able to create personalized watchlists with up to 50 stocks and receive instant notifications when prices cross specified thresholds. The notification system must be reliable and fast.",
        "The system must support at least 10,000 concurrent users and maintain response times under 2 seconds for all queries. Database performance should be optimized for high-frequency trading scenarios.",
        "All user data and trading information must be encrypted using AES-256 encryption. The system should comply with financial regulations including SOX and GDPR requirements.",
        "The system should integrate with popular trading platforms like MetaTrader 4, TradingView, and Bloomberg Terminal through secure APIs. Integration should be seamless and require minimal configuration."
    ]
    
    for i, req in enumerate(sample_requirements, 1):
        file_path = f"data/input/requirement_{i:02d}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(req)
        print(f"  Created {file_path}")
    
    print(f"Created {len(sample_requirements)} sample requirement files")

def run_quick_test():
    """Run a quick test of the system"""
    print("\nRunning quick test...")
    
    try:
        # Import our modules
        from module1_large_scale import RequirementsProcessor, Config
        
        # Initialize processor
        config = Config()
        processor = RequirementsProcessor(config)
        
        # Test with sample text
        test_text = "The system must provide real-time stock price updates and allow users to create personalized watchlists."
        
        print(f"Processing: {test_text}")
        
        result = processor.process_single_requirement({
            'type': 'text',
            'content': test_text
        })
        
        print(f"\nResult:")
        print(f"  Status: {result.get('status')}")
        print(f"  Ambiguities: {len(result.get('ambiguities', []))}")
        print(f"  Extracted fields: {len(result.get('extracted_fields', {}))}")
        
        if result.get('ambiguities'):
            print(f"\nAmbiguous terms:")
            for ambiguity in result['ambiguities']:
                print(f"  - '{ambiguity['word']}' ({ambiguity['category']})")
        
        if result.get('extracted_fields'):
            print(f"\nExtracted fields:")
            for field, value in result['extracted_fields'].items():
                print(f"  {field}: {value}")
        
        print("\n✅ Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Quick test failed: {str(e)}")
        return False

def run_batch_test():
    """Run a batch processing test"""
    print("\nRunning batch processing test...")
    
    try:
        from batch_processor import BatchProcessor
        from module1_large_scale import Config
        
        config = Config()
        batch_processor = BatchProcessor(config)
        
        # Process the sample data we created
        results = batch_processor.process_directory("data/input")
        
        print(f"Batch processing results:")
        print(f"  Total files processed: {len(results)}")
        
        successful = [r for r in results if r.get('status') == 'completed']
        failed = [r for r in results if r.get('status') == 'failed']
        
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        
        if successful:
            total_ambiguities = sum(len(r.get('ambiguities', [])) for r in successful)
            print(f"  Total ambiguities found: {total_ambiguities}")
        
        # Save results
        with open("data/output/batch_test_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"  Results saved to: data/output/batch_test_results.json")
        print("\n✅ Batch test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Batch test failed: {str(e)}")
        return False

def run_srs_test():
    """Run SRS generation test"""
    print("\nRunning SRS generation test...")
    
    try:
        from srs_generator import SRSGenerator
        
        # Load batch results
        with open("data/output/batch_test_results.json", 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        # Generate SRS
        generator = SRSGenerator()
        project_info = {
            'title': 'Stock Prediction System - SRS',
            'author': 'Requirements Engineering Team',
            'version': '1.0'
        }
        
        srs = generator.generate_srs(results, project_info)
        
        # Export SRS
        json_file = generator.export_to_json(srs, "data/output/test_srs.json")
        html_file = generator.export_to_html(srs, "data/output/test_srs.html")
        
        print(f"Initial SRS generated (Module 1 scope):")
        print(f"  Document ID: {srs.document_id}")
        print(f"  Title: {srs.title}")
        print(f"  Contains: Introduction and Overall Description sections only")
        print(f"  JSON file: {json_file}")
        print(f"  HTML file: {html_file}")
        
        print("\n✅ SRS test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ SRS test failed: {str(e)}")
        return False

def main():
    """Main quick start function"""
    print("LARGE SCALE REQUIREMENTS ENGINEERING SYSTEM - QUICK START")
    print("=" * 70)
    
    # Check system requirements
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    if not check_spacy_model():
        print("\n❌ Please install spaCy model first")
        return
    
    # Create sample data
    create_sample_data()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if run_quick_test():
        tests_passed += 1
    
    if run_batch_test():
        tests_passed += 1
    
    if run_srs_test():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("QUICK START SUMMARY")
    print("=" * 70)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! The system is ready for use.")
        print("\nNext steps:")
        print("1. Add your own requirements files to data/input/")
        print("2. Run: python main_orchestrator.py --mode batch --input_dir data/input")
        print("3. Generate SRS: python main_orchestrator.py --mode srs")
        print("4. Check results in data/output/")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} tests failed. Please check the errors above.")
    
    print(f"\nFor more information, see README_LARGE_SCALE.md")

if __name__ == "__main__":
    main()

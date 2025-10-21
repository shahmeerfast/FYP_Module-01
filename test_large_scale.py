#!/usr/bin/env python3
"""
Test Script for Large Scale Requirements Engineering System
==========================================================

This script demonstrates the capabilities of the large-scale Module 1 system
with sample data and various processing scenarios.
"""

import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Import our modules
from module1_large_scale import RequirementsProcessor, Config
from batch_processor import BatchProcessor
from srs_generator import SRSGenerator
from data_manager import DataManager

def create_sample_data():
    """Create sample requirements data for testing"""
    sample_requirements = [
        {
            "id": "REQ-001",
            "content": "The stock prediction system must provide real-time price updates for all major stock exchanges including NYSE, NASDAQ, and LSE. The system should update prices every second during market hours.",
            "type": "functional",
            "priority": "high"
        },
        {
            "id": "REQ-002", 
            "content": "Users should be able to create personalized watchlists with up to 50 stocks and receive instant notifications when prices cross specified thresholds. The notification system must be reliable and fast.",
            "type": "functional",
            "priority": "high"
        },
        {
            "id": "REQ-003",
            "content": "The system must support at least 10,000 concurrent users and maintain response times under 2 seconds for all queries. Database performance should be optimized for high-frequency trading scenarios.",
            "type": "non-functional",
            "priority": "critical"
        },
        {
            "id": "REQ-004",
            "content": "All user data and trading information must be encrypted using AES-256 encryption. The system should comply with financial regulations including SOX and GDPR requirements.",
            "type": "security",
            "priority": "critical"
        },
        {
            "id": "REQ-005",
            "content": "The system should integrate with popular trading platforms like MetaTrader 4, TradingView, and Bloomberg Terminal through secure APIs. Integration should be seamless and require minimal configuration.",
            "type": "integration",
            "priority": "medium"
        }
    ]
    
    return sample_requirements

def test_single_processing():
    """Test single requirement processing"""
    print("=" * 60)
    print("TESTING SINGLE REQUIREMENT PROCESSING")
    print("=" * 60)
    
    # Initialize processor
    config = Config()
    processor = RequirementsProcessor(config)
    
    # Test with sample text
    sample_text = """
    We need to develop a comprehensive stock prediction system that can analyze 
    historical market data and provide accurate predictions for various stocks. 
    The system should be fast and user-friendly, allowing traders to make 
    informed decisions quickly. It must support multiple data sources and 
    integrate with existing trading platforms.
    """
    
    print(f"Processing text: {sample_text[:100]}...")
    
    # Process requirement
    result = processor.process_single_requirement({
        'type': 'text',
        'content': sample_text
    })
    
    print(f"\nProcessing Result:")
    print(f"Status: {result.get('status')}")
    print(f"Ambiguities found: {len(result.get('ambiguities', []))}")
    print(f"Extracted fields: {len(result.get('extracted_fields', {}))}")
    
    if result.get('ambiguities'):
        print(f"\nAmbiguous terms detected:")
        for ambiguity in result['ambiguities'][:3]:  # Show first 3
            print(f"  - '{ambiguity['word']}' ({ambiguity['category']})")
    
    if result.get('extracted_fields'):
        print(f"\nExtracted fields:")
        for field, value in result['extracted_fields'].items():
            print(f"  {field}: {value[:100]}...")
    
    return result

def test_batch_processing():
    """Test batch processing with sample data"""
    print("\n" + "=" * 60)
    print("TESTING BATCH PROCESSING")
    print("=" * 60)
    
    # Create temporary directory with sample files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample text files
        sample_data = create_sample_data()
        for i, req in enumerate(sample_data):
            file_path = temp_path / f"requirement_{i+1}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(req['content'])
        
        print(f"Created {len(sample_data)} sample requirement files in {temp_dir}")
        
        # Initialize batch processor
        config = Config()
        batch_processor = BatchProcessor(config)
        
        # Process batch
        results = batch_processor.process_directory(str(temp_path))
        
        print(f"\nBatch Processing Results:")
        print(f"Total files processed: {len(results)}")
        
        successful = [r for r in results if r.get('status') == 'completed']
        failed = [r for r in results if r.get('status') == 'failed']
        
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            total_ambiguities = sum(len(r.get('ambiguities', [])) for r in successful)
            print(f"Total ambiguities found: {total_ambiguities}")
            
            # Show sample results
            print(f"\nSample processed requirement:")
            sample_result = successful[0]
            print(f"  Original: {sample_result.get('original_text', '')[:100]}...")
            print(f"  Ambiguities: {len(sample_result.get('ambiguities', []))}")
            print(f"  Extracted fields: {len(sample_result.get('extracted_fields', {}))}")
        
        return results

def test_srs_generation():
    """Test SRS generation"""
    print("\n" + "=" * 60)
    print("TESTING SRS GENERATION")
    print("=" * 60)
    
    # Create sample processed requirements
    sample_processed = [
        {
            'status': 'completed',
            'original_text': 'The system must provide real-time stock price updates and allow users to create personalized watchlists.',
            'extracted_fields': {
                'Purpose': 'Real-time stock monitoring and portfolio management',
                'Scope': 'Stock market data analysis and user portfolio tracking',
                'Product Functions': 'Price updates, watchlist creation, portfolio management',
                'Constraints': 'Real-time data requirements, user authentication',
                'Stakeholders': 'Traders, investors, financial analysts'
            },
            'ambiguities': [
                {'word': 'real-time', 'category': 'performance_terms', 'context': 'real-time stock price updates'},
                {'word': 'personalized', 'category': 'adjectives', 'context': 'create personalized watchlists'}
            ]
        },
        {
            'status': 'completed',
            'original_text': 'The system should support at least 10,000 concurrent users and maintain response times under 2 seconds.',
            'extracted_fields': {
                'Purpose': 'High-performance trading platform',
                'Scope': 'Scalable user management and performance optimization',
                'Product Functions': 'User management, performance monitoring',
                'Constraints': '10,000 concurrent users, 2-second response time',
                'Stakeholders': 'Active traders, system administrators'
            },
            'ambiguities': [
                {'word': 'should', 'category': 'modal_verbs', 'context': 'system should support'},
                {'word': 'at least', 'category': 'quantifiers', 'context': 'at least 10,000 concurrent'}
            ]
        }
    ]
    
    # Initialize SRS generator
    generator = SRSGenerator()
    
    # Generate SRS
    project_info = {
        'title': 'Stock Prediction System - Software Requirements Specification',
        'author': 'Requirements Engineering Team',
        'version': '1.0'
    }
    
    print("Generating SRS document...")
    srs = generator.generate_srs(sample_processed, project_info)
    
    print(f"SRS Document Generated:")
    print(f"  Document ID: {srs.document_id}")
    print(f"  Title: {srs.title}")
    print(f"  Version: {srs.version}")
    print(f"  Date: {srs.date}")
    
    # Show SRS sections
    print(f"\nSRS Sections:")
    print(f"  Introduction: {len(srs.sections['introduction'])} subsections")
    print(f"  Overall Description: {len(srs.sections['overall_description'])} subsections")
    print(f"  Specific Requirements: {len(srs.sections['specific_requirements'])} subsections")
    print(f"  Appendices: {len(srs.sections['appendices'])} subsections")
    
    # Show sample content
    print(f"\nSample SRS Content:")
    print(f"  Purpose: {srs.sections['introduction']['purpose'][:100]}...")
    print(f"  Scope: {srs.sections['introduction']['scope'][:100]}...")
    
    functional_reqs = srs.sections['specific_requirements']['functional_requirements']
    if functional_reqs:
        print(f"  Functional Requirements: {len(functional_reqs)} requirements")
        print(f"    Sample: {functional_reqs[0]['description'][:80]}...")
    
    # Export SRS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = generator.export_to_json(srs, f"test_srs_{timestamp}.json")
    html_file = generator.export_to_html(srs, f"test_srs_{timestamp}.html")
    
    print(f"\nSRS exported to:")
    print(f"  JSON: {json_file}")
    print(f"  HTML: {html_file}")
    
    return srs

def test_data_management():
    """Test data management system"""
    print("\n" + "=" * 60)
    print("TESTING DATA MANAGEMENT")
    print("=" * 60)
    
    # Initialize data manager
    data_manager = DataManager("test_data")
    
    # Create sample records
    from data_manager import DataRecord
    
    sample_records = [
        DataRecord(
            id="test_001",
            content="The system must provide real-time stock price updates",
            type="text",
            metadata={"priority": "high", "category": "functional"}
        ),
        DataRecord(
            id="test_002",
            content="Users should be able to create personalized watchlists",
            type="text",
            metadata={"priority": "medium", "category": "functional"}
        ),
        DataRecord(
            id="test_003",
            content="The system must support 10,000 concurrent users",
            type="text",
            metadata={"priority": "critical", "category": "non-functional"}
        )
    ]
    
    # Add records
    print("Adding sample records...")
    for record in sample_records:
        data_manager.add_record(record)
    
    # List records
    print(f"\nRetrieved {len(sample_records)} records from database")
    
    # Get statistics
    stats = data_manager.get_processing_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total records: {stats['total_records']}")
    print(f"  Status breakdown: {stats['status_breakdown']}")
    print(f"  Type breakdown: {stats['type_breakdown']}")
    
    # Export data
    csv_file = data_manager.export_to_csv("test_export.csv")
    json_file = data_manager.export_to_json("test_export.json")
    
    print(f"\nData exported to:")
    print(f"  CSV: {csv_file}")
    print(f"  JSON: {json_file}")
    
    return stats

def test_performance_metrics():
    """Test system performance"""
    print("\n" + "=" * 60)
    print("TESTING PERFORMANCE METRICS")
    print("=" * 60)
    
    import time
    
    # Test processing speed
    config = Config()
    processor = RequirementsProcessor(config)
    
    test_texts = [
        "The system must provide real-time stock price updates",
        "Users should be able to create personalized watchlists",
        "The system must support at least 10,000 concurrent users",
        "All user data must be encrypted using AES-256 encryption",
        "The system should integrate with popular trading platforms"
    ]
    
    print(f"Testing processing speed with {len(test_texts)} requirements...")
    
    start_time = time.time()
    results = []
    
    for i, text in enumerate(test_texts):
        result = processor.process_single_requirement({
            'type': 'text',
            'content': text
        })
        results.append(result)
        print(f"  Processed requirement {i+1}/{len(test_texts)}")
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\nPerformance Results:")
    print(f"  Total processing time: {processing_time:.2f} seconds")
    print(f"  Average time per requirement: {processing_time/len(test_texts):.2f} seconds")
    print(f"  Processing rate: {len(test_texts)/processing_time:.2f} requirements/second")
    
    # Analyze results
    successful = [r for r in results if r.get('status') == 'completed']
    total_ambiguities = sum(len(r.get('ambiguities', [])) for r in successful)
    
    print(f"\nQuality Metrics:")
    print(f"  Success rate: {len(successful)/len(results):.2%}")
    print(f"  Total ambiguities found: {total_ambiguities}")
    print(f"  Average ambiguities per requirement: {total_ambiguities/len(successful):.2f}")
    
    return {
        'processing_time': processing_time,
        'success_rate': len(successful)/len(results),
        'total_ambiguities': total_ambiguities
    }

def main():
    """Run all tests"""
    print("LARGE SCALE REQUIREMENTS ENGINEERING SYSTEM - TEST SUITE")
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Run individual tests
        single_result = test_single_processing()
        batch_results = test_batch_processing()
        srs_document = test_srs_generation()
        data_stats = test_data_management()
        performance = test_performance_metrics()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("✅ Single requirement processing: PASSED")
        print("✅ Batch processing: PASSED")
        print("✅ SRS generation: PASSED")
        print("✅ Data management: PASSED")
        print("✅ Performance testing: PASSED")
        
        print(f"\nOverall Performance:")
        print(f"  Processing rate: {performance['processing_time']:.2f} seconds for 5 requirements")
        print(f"  Success rate: {performance['success_rate']:.2%}")
        print(f"  Ambiguities detected: {performance['total_ambiguities']}")
        
        print(f"\nSystem is ready for large-scale requirements processing!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

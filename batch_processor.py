#!/usr/bin/env python3
"""
Batch Processor for Large Scale Requirements Processing
======================================================

This script handles batch processing of large datasets for Module 1.
It can process multiple files, directories, and different input formats.

Usage:
    python batch_processor.py --input_dir data/input --output_dir data/output
    python batch_processor.py --input_file requirements.txt --output_file results.json
"""

import argparse
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

from module1_large_scale import RequirementsProcessor, Config

class BatchProcessor:
    """Handles batch processing of requirements data"""
    
    def __init__(self, config: Config):
        self.config = config
        self.processor = RequirementsProcessor(config)
        self.logger = logging.getLogger(__name__)
    
    def process_directory(self, input_dir: str, file_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """
        Process all files in a directory matching given patterns
        
        Args:
            input_dir: Directory containing input files
            file_patterns: List of file extensions to process (e.g., ['.txt', '.wav'])
        
        Returns:
            List of processing results
        """
        if file_patterns is None:
            file_patterns = ['.txt', '.wav', '.mp3', '.m4a', '.flac', '.json']
        
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory {input_dir} not found")
        
        # Find all matching files
        files_to_process = []
        for pattern in file_patterns:
            files_to_process.extend(input_path.glob(f"**/*{pattern}"))
        
        self.logger.info(f"Found {len(files_to_process)} files to process")
        
        # Process files
        results = []
        for file_path in files_to_process:
            try:
                self.logger.info(f"Processing {file_path}")
                
                # Determine input type and prepare data
                if file_path.suffix.lower() in ['.wav', '.mp3', '.m4a', '.flac']:
                    input_data = {'type': 'audio', 'file_path': str(file_path)}
                else:
                    # Text file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    input_data = {'type': 'text', 'content': content}
                
                # Process
                result = self.processor.process_single_requirement(input_data)
                result['source_file'] = str(file_path)
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {str(e)}")
                results.append({
                    'source_file': str(file_path),
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results
    
    def process_csv_file(self, csv_file: str, text_column: str = 'text') -> List[Dict[str, Any]]:
        """
        Process requirements from a CSV file
        
        Args:
            csv_file: Path to CSV file
            text_column: Name of column containing text data
        
        Returns:
            List of processing results
        """
        df = pd.read_csv(csv_file)
        
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in CSV file")
        
        results = []
        for idx, row in df.iterrows():
            try:
                self.logger.info(f"Processing row {idx + 1}/{len(df)}")
                
                input_data = {
                    'type': 'text',
                    'content': str(row[text_column])
                }
                
                result = self.processor.process_single_requirement(input_data)
                result['row_index'] = idx
                result['source_file'] = csv_file
                
                # Add any additional columns from CSV
                for col in df.columns:
                    if col != text_column:
                        result[f'csv_{col}'] = row[col]
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing row {idx}: {str(e)}")
                results.append({
                    'row_index': idx,
                    'source_file': csv_file,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results
    
    def process_json_file(self, json_file: str) -> List[Dict[str, Any]]:
        """
        Process requirements from a JSON file
        
        Args:
            json_file: Path to JSON file
        
        Returns:
            List of processing results
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            requirements = data
        elif isinstance(data, dict) and 'requirements' in data:
            requirements = data['requirements']
        else:
            requirements = [data]
        
        results = []
        for idx, req in enumerate(requirements):
            try:
                self.logger.info(f"Processing requirement {idx + 1}/{len(requirements)}")
                
                # Determine input type
                if 'file_path' in req:
                    input_data = {'type': 'audio', 'file_path': req['file_path']}
                elif 'content' in req:
                    input_data = {'type': 'text', 'content': req['content']}
                else:
                    raise ValueError("Requirement must have either 'file_path' or 'content'")
                
                result = self.processor.process_single_requirement(input_data)
                result['requirement_index'] = idx
                result['source_file'] = json_file
                
                # Preserve original requirement data
                result['original_requirement'] = req
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing requirement {idx}: {str(e)}")
                results.append({
                    'requirement_index': idx,
                    'source_file': json_file,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary report of processing results"""
        total_processed = len(results)
        successful = len([r for r in results if r.get('status') == 'completed'])
        failed = len([r for r in results if r.get('status') == 'failed'])
        
        # Count ambiguities
        total_ambiguities = sum(len(r.get('ambiguities', [])) for r in results if r.get('status') == 'completed')
        
        # Count extracted fields
        fields_count = {}
        for result in results:
            if result.get('status') == 'completed':
                for field in result.get('extracted_fields', {}):
                    fields_count[field] = fields_count.get(field, 0) + 1
        
        return {
            'summary': {
                'total_processed': total_processed,
                'successful': successful,
                'failed': failed,
                'success_rate': successful / total_processed if total_processed > 0 else 0,
                'total_ambiguities': total_ambiguities,
                'avg_ambiguities_per_requirement': total_ambiguities / successful if successful > 0 else 0
            },
            'field_extraction_stats': fields_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str = None) -> str:
        """Save results to file with summary report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.config.output_dir}/batch_results_{timestamp}.json"
        
        # Generate summary
        summary = self.generate_summary_report(results)
        
        # Combine results and summary
        output_data = {
            'summary': summary,
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {output_file}")
        return output_file

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Batch process requirements data')
    parser.add_argument('--input_dir', help='Input directory containing files to process')
    parser.add_argument('--input_file', help='Single input file to process')
    parser.add_argument('--output_file', help='Output file for results')
    parser.add_argument('--file_patterns', nargs='+', 
                       default=['.txt', '.wav', '.mp3', '.m4a', '.flac', '.json'],
                       help='File patterns to process')
    parser.add_argument('--text_column', default='text',
                       help='Column name for text data in CSV files')
    parser.add_argument('--config_file', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = Config()
    if args.config_file:
        # Load custom config if provided
        pass  # Implement config loading if needed
    
    # Initialize processor
    processor = BatchProcessor(config)
    
    results = []
    
    try:
        if args.input_dir:
            # Process directory
            results = processor.process_directory(args.input_dir, args.file_patterns)
        elif args.input_file:
            # Process single file
            file_path = Path(args.input_file)
            if file_path.suffix.lower() == '.csv':
                results = processor.process_csv_file(args.input_file, args.text_column)
            elif file_path.suffix.lower() == '.json':
                results = processor.process_json_file(args.input_file)
            else:
                # Treat as text file
                with open(args.input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                input_data = {'type': 'text', 'content': content}
                result = processor.processor.process_single_requirement(input_data)
                result['source_file'] = args.input_file
                results = [result]
        else:
            print("Please specify either --input_dir or --input_file")
            return
        
        # Save results
        output_file = processor.save_results(results, args.output_file)
        
        # Print summary
        summary = processor.generate_summary_report(results)
        print(f"\nProcessing Summary:")
        print(f"Total processed: {summary['summary']['total_processed']}")
        print(f"Successful: {summary['summary']['successful']}")
        print(f"Failed: {summary['summary']['failed']}")
        print(f"Success rate: {summary['summary']['success_rate']:.2%}")
        print(f"Total ambiguities found: {summary['summary']['total_ambiguities']}")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        logging.error(f"Error in batch processing: {str(e)}")
        raise

if __name__ == "__main__":
    main()

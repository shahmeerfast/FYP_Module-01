#!/usr/bin/env python3
"""
Simple SRS Generator for Ali requirement
"""

import json
from srs_generator import SRSGenerator

def main():
    # Load the Ali requirement data
    with open('data/output/ali_requirement.json', 'r', encoding='utf-8') as f:
        requirements_data = json.load(f)
    
    # Project info
    project_info = {
        'title': 'Ali',
        'author': 'shahmeer',
        'version': '1.0'
    }
    
    # Generate SRS
    generator = SRSGenerator()
    srs = generator.generate_srs(requirements_data, project_info)
    
    # Export to files
    json_file = generator.export_to_json(srs, "srs_ali.json")
    html_file = generator.export_to_html(srs, "srs_ali.html")
    
    print(f"SRS generated successfully for Ali!")
    print(f"JSON file: {json_file}")
    print(f"HTML file: {html_file}")
    
    # Print the content to verify it's correct
    print("\n=== SRS Content ===")
    print(f"Title: {srs.title}")
    print(f"Author: {srs.author}")
    print(f"Purpose: {srs.sections['introduction']['purpose']}")
    print(f"Scope: {srs.sections['introduction']['scope']}")
    print(f"Definitions: {srs.sections['introduction']['definitions']}")
    print(f"Product Functions: {srs.sections['overall_description']['product_functions']}")
    print(f"User Characteristics: {srs.sections['overall_description']['user_characteristics']}")

if __name__ == "__main__":
    main()

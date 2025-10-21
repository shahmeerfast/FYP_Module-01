#!/usr/bin/env python3
"""
IEEE 830-Compliant SRS Generator
================================

This module generates IEEE 830-compliant Software Requirements Specification (SRS)
documents from processed requirements data.

IEEE 830 Standard Structure:
1. Introduction
2. Overall Description
3. Specific Requirements
4. Appendices
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SRSDocument:
    """Represents an IEEE 830-compliant SRS document"""
    document_id: str
    title: str
    version: str
    date: str
    author: str
    sections: Dict[str, Any]

class SRSGenerator:
    """Generates IEEE 830-compliant SRS documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.template = self._load_srs_template()
    
    def _load_srs_template(self) -> Dict[str, Any]:
        """Load the SRS template structure - Module 1 focuses only on Introduction and Overall Description"""
        return {
            "introduction": {
                "purpose": "",
                "scope": "",
                "definitions": [],
                "references": [],
                "overview": ""
            },
            "overall_description": {
                "product_perspective": "",
                "product_functions": [],
                "user_characteristics": [],
                "constraints": [],
                "assumptions": [],
                "dependencies": []
            }
        }
    
    def generate_srs(self, requirements_data: List[Dict[str, Any]], 
                    project_info: Dict[str, str] = None) -> SRSDocument:
        """
        Generate a complete SRS document from requirements data
        
        Args:
            requirements_data: List of processed requirements
            project_info: Project metadata (title, author, etc.)
        
        Returns:
            Complete SRS document
        """
        if project_info is None:
            project_info = {
                'title': 'Software Requirements Specification',
                'author': 'Requirements Engineering System',
                'version': '1.0'
            }
        
        # Initialize SRS document
        srs = SRSDocument(
            document_id=f"SRS-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=project_info.get('title', 'Software Requirements Specification'),
            version=project_info.get('version', '1.0'),
            date=datetime.now().strftime('%Y-%m-%d'),
            author=project_info.get('author', 'Requirements Engineering System'),
            sections=self.template.copy()
        )
        
        # Process requirements data
        self._process_requirements_data(requirements_data, srs)
        
        # Generate document sections (Module 1 focuses only on Introduction and Overall Description)
        self._generate_introduction(srs)
        self._generate_overall_description(srs)
        
        return srs
    
    def _process_requirements_data(self, requirements_data: List[Dict[str, Any]], srs: SRSDocument):
        """Process and categorize requirements data"""
        # Collect all extracted fields
        all_fields = []
        all_ambiguities = []
        all_text = []
        
        for req in requirements_data:
            if req.get('status') == 'completed':
                all_fields.append(req.get('extracted_fields', {}))
                all_ambiguities.extend(req.get('ambiguities', []))
                all_text.append(req.get('original_text', ''))
        
        # Store processed data
        srs.sections['_processed_data'] = {
            'all_fields': all_fields,
            'all_ambiguities': all_ambiguities,
            'all_text': all_text,
            'total_requirements': len(requirements_data),
            'successful_requirements': len([r for r in requirements_data if r.get('status') == 'completed'])
        }
    
    def _generate_introduction(self, srs: SRSDocument):
        """Generate Introduction section"""
        data = srs.sections['_processed_data']
        
        # Purpose - combine all purposes, but clean up malformed text
        purposes = [fields.get('Purpose', '') for fields in data['all_fields'] if fields.get('Purpose')]
        cleaned_purposes = [self._clean_extracted_text(purpose) for purpose in purposes if purpose]
        
        if cleaned_purposes:
            srs.sections['introduction']['purpose'] = self._merge_text(cleaned_purposes)
        else:
            # Fallback: extract from original text
            srs.sections['introduction']['purpose'] = self._extract_purpose_from_original_text(data['all_text'])
        
        # Scope - combine all scopes, but clean up malformed text
        scopes = [fields.get('Scope', '') for fields in data['all_fields'] if fields.get('Scope')]
        cleaned_scopes = [self._clean_extracted_text(scope) for scope in scopes if scope]
        
        if cleaned_scopes:
            srs.sections['introduction']['scope'] = self._merge_text(cleaned_scopes)
        else:
            # Fallback: extract from original text
            srs.sections['introduction']['scope'] = self._extract_scope_from_original_text(data['all_text'])
        
        # Definitions - extract from all text
        definitions = self._extract_definitions(data['all_text'])
        srs.sections['introduction']['definitions'] = definitions
        
        # Overview
        srs.sections['introduction']['overview'] = (
            f"This document specifies the requirements for the system based on "
            f"{data['successful_requirements']} processed requirements. "
            f"The system is designed to meet the functional and non-functional "
            f"requirements outlined in the following sections."
        )
    
    def _generate_overall_description(self, srs: SRSDocument):
        """Generate Overall Description section"""
        data = srs.sections['_processed_data']
        
        # Product Functions - extract from fields or fallback to original text
        functions = []
        for fields in data['all_fields']:
            if fields.get('Product Functions'):
                cleaned_func = self._clean_extracted_text(fields['Product Functions'])
                if cleaned_func:
                    functions.extend(self._parse_functions(cleaned_func))
        
        if not functions:
            functions = self._extract_functions_from_original_text(data['all_text'])
        
        srs.sections['overall_description']['product_functions'] = list(set(functions))
        
        # User Characteristics - extract from fields or fallback to original text
        stakeholders = []
        for fields in data['all_fields']:
            if fields.get('Stakeholders'):
                cleaned_stake = self._clean_extracted_text(fields['Stakeholders'])
                if cleaned_stake:
                    stakeholders.extend(self._parse_stakeholders(cleaned_stake))
        
        if not stakeholders:
            stakeholders = self._extract_stakeholders_from_original_text(data['all_text'])
        
        srs.sections['overall_description']['user_characteristics'] = list(set(stakeholders))
        
        # Constraints - extract from fields or fallback to original text
        constraints = []
        for fields in data['all_fields']:
            if fields.get('Constraints'):
                cleaned_const = self._clean_extracted_text(fields['Constraints'])
                if cleaned_const:
                    constraints.extend(self._parse_constraints(cleaned_const))
        
        if not constraints:
            constraints = self._extract_constraints_from_original_text(data['all_text'])
        
        srs.sections['overall_description']['constraints'] = list(set(constraints))
        
        # Dependencies - extract from fields or fallback to original text
        dependencies = []
        for fields in data['all_fields']:
            if fields.get('Dependencies'):
                cleaned_dep = self._clean_extracted_text(fields['Dependencies'])
                if cleaned_dep:
                    dependencies.extend(self._parse_dependencies(cleaned_dep))
        
        if not dependencies:
            dependencies = self._extract_dependencies_from_original_text(data['all_text'])
        
        srs.sections['overall_description']['dependencies'] = list(set(dependencies))
        
        # Assumptions - extract from fields or fallback to original text
        assumptions = []
        for fields in data['all_fields']:
            if fields.get('Assumptions'):
                cleaned_assum = self._clean_extracted_text(fields['Assumptions'])
                if cleaned_assum:
                    assumptions.extend(self._parse_assumptions(cleaned_assum))
        
        if not assumptions:
            assumptions = ['System requirements are clearly defined', 'Stakeholders are available for consultation']
        
        srs.sections['overall_description']['assumptions'] = list(set(assumptions))
    
    # Note: Module 1 focuses only on Introduction and Overall Description sections
    # Specific Requirements and Appendices are generated in later modules
    
    def _merge_text(self, text_list: List[str]) -> str:
        """Merge multiple text strings into one coherent text"""
        # Remove empty strings and duplicates
        filtered = [text.strip() for text in text_list if text.strip()]
        unique = list(dict.fromkeys(filtered))  # Remove duplicates while preserving order
        
        if not unique:
            return "To be defined"
        
        if len(unique) == 1:
            return unique[0]
        
        # Merge multiple texts
        return ". ".join(unique) + "."
    
    def _extract_definitions(self, text_list: List[str]) -> List[str]:
        """Extract key terms and definitions from text"""
        definitions = set()
        
        for text in text_list:
            # Simple extraction of technical terms (can be enhanced with NLP)
            words = text.split()
            for i, word in enumerate(words):
                if len(word) > 5 and word.isalpha():
                    # Look for definition patterns
                    if i < len(words) - 2 and words[i+1] in ['is', 'are', 'refers', 'means']:
                        definition = f"{word}: {' '.join(words[i+2:i+10])}"
                        definitions.add(definition)
        
        return list(definitions)[:20]  # Limit to 20 definitions
    
    def _parse_functions(self, functions_text: str) -> List[str]:
        """Parse product functions from text"""
        # Split by common separators
        functions = []
        for separator in ['.', ';', '\n', ',']:
            if separator in functions_text:
                functions = [f.strip() for f in functions_text.split(separator) if f.strip()]
                break
        
        if not functions:
            functions = [functions_text]
        
        return functions
    
    def _parse_stakeholders(self, stakeholders_text: str) -> List[str]:
        """Parse stakeholders from text"""
        return self._parse_functions(stakeholders_text)
    
    def _parse_constraints(self, constraints_text: str) -> List[str]:
        """Parse constraints from text"""
        return self._parse_functions(constraints_text)
    
    def _parse_dependencies(self, dependencies_text: str) -> List[str]:
        """Parse dependencies from text"""
        return self._parse_functions(dependencies_text)
    
    def _parse_assumptions(self, assumptions_text: str) -> List[str]:
        """Parse assumptions from text"""
        return self._parse_functions(assumptions_text)
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean malformed extracted text from AI models"""
        if not text:
            return ""
        
        # Remove numbered lists and malformed patterns
        import re
        
        # Remove patterns like "2. scope or boundaries of this system 3. ..."
        text = re.sub(r'\d+\.\s*[^.]*?(?=\d+\.|$)', '', text)
        
        # Remove patterns like "2. unknown 3. ..."
        text = re.sub(r'\d+\.\s*unknown\s*\d+\.', '', text)
        
        # Clean up multiple spaces and periods
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\.+', '.', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # If text is too short or contains only numbers, return empty
        if len(text) < 10 or text.isdigit():
            return ""
        
        return text
    
    def _extract_purpose_from_original_text(self, text_list: List[str]) -> str:
        """Extract purpose from original text when AI extraction fails"""
        all_text = ' '.join(text_list)
        
        # Look for purpose indicators
        purpose_indicators = ['must', 'should', 'need to', 'require', 'provide', 'allow', 'enable']
        sentences = all_text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in purpose_indicators):
                return sentence.capitalize()
        
        return "System requirements specification and implementation"
    
    def _extract_scope_from_original_text(self, text_list: List[str]) -> str:
        """Extract scope from original text when AI extraction fails"""
        all_text = ' '.join(text_list)
        
        # Look for scope indicators
        scope_indicators = ['system', 'application', 'platform', 'service', 'tool']
        sentences = all_text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence.lower() for indicator in scope_indicators):
                return sentence.capitalize()
        
        return "Complete system implementation and deployment"
    
    def _extract_functions_from_original_text(self, text_list: List[str]) -> List[str]:
        """Extract functions from original text when AI extraction fails"""
        functions = []
        function_indicators = ['provide', 'allow', 'enable', 'support', 'create', 'manage', 'track', 'update']
        
        for text in text_list:
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(indicator in sentence.lower() for indicator in function_indicators):
                    # Extract the main action
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if word.lower() in function_indicators and i < len(words) - 1:
                            # Extract the function description
                            func_desc = ' '.join(words[i:i+5])  # Take next 5 words
                            functions.append(func_desc)
                            break
        
        return functions[:5] if functions else ['Core system functionality']
    
    def _extract_stakeholders_from_original_text(self, text_list: List[str]) -> List[str]:
        """Extract stakeholders from original text when AI extraction fails"""
        stakeholders = []
        stakeholder_indicators = ['user', 'admin', 'trader', 'investor', 'analyst', 'customer', 'client']
        
        all_text = ' '.join(text_list).lower()
        words = all_text.split()
        
        for word in words:
            if word in stakeholder_indicators:
                stakeholders.append(word.capitalize())
        
        return list(set(stakeholders)) if stakeholders else ['System users']
    
    def _extract_constraints_from_original_text(self, text_list: List[str]) -> List[str]:
        """Extract constraints from original text when AI extraction fails"""
        constraints = []
        constraint_indicators = ['must', 'should', 'require', 'limit', 'constraint', 'restriction', 'under', 'at least']
        
        for text in text_list:
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(indicator in sentence.lower() for indicator in constraint_indicators):
                    constraints.append(sentence)
        
        return constraints[:3] if constraints else ['System performance requirements']
    
    def _extract_dependencies_from_original_text(self, text_list: List[str]) -> List[str]:
        """Extract dependencies from original text when AI extraction fails"""
        dependencies = []
        dependency_indicators = ['integrate', 'connect', 'api', 'database', 'external', 'platform', 'service']
        
        for text in text_list:
            sentences = text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(indicator in sentence.lower() for indicator in dependency_indicators):
                    dependencies.append(sentence)
        
        return dependencies[:3] if dependencies else ['External system integration']
    
    # Note: Functional requirements, non-functional requirements, performance requirements,
    # interface requirements, glossary, and acronyms extraction methods are removed
    # as they are not part of Module 1's scope (Introduction and Overall Description only)
    
    def export_to_json(self, srs: SRSDocument, output_file: str = None) -> str:
        """Export SRS to JSON format"""
        if output_file is None:
            output_file = f"srs_{srs.document_id}.json"
        
        # Convert to dictionary
        srs_dict = {
            'document_id': srs.document_id,
            'title': srs.title,
            'version': srs.version,
            'date': srs.date,
            'author': srs.author,
            'sections': srs.sections
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(srs_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"SRS exported to {output_file}")
        return output_file
    
    def export_to_html(self, srs: SRSDocument, output_file: str = None) -> str:
        """Export SRS to HTML format"""
        if output_file is None:
            output_file = f"srs_{srs.document_id}.html"
        
        html_content = self._generate_html(srs)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"SRS exported to {output_file}")
        return output_file
    
    def _generate_html(self, srs: SRSDocument) -> str:
        """Generate HTML content for SRS"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{srs.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .metadata {{ background-color: #ecf0f1; padding: 15px; margin-bottom: 20px; }}
        .requirement {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #3498db; }}
        .requirement-id {{ font-weight: bold; color: #2c3e50; }}
        ul {{ margin: 10px 0; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>{srs.title}</h1>
    
    <div class="metadata">
        <p><strong>Document ID:</strong> {srs.document_id}</p>
        <p><strong>Version:</strong> {srs.version}</p>
        <p><strong>Date:</strong> {srs.date}</p>
        <p><strong>Author:</strong> {srs.author}</p>
    </div>
    
    <h2>1. Introduction</h2>
    <h3>1.1 Purpose</h3>
    <p>{srs.sections['introduction']['purpose']}</p>
    
    <h3>1.2 Scope</h3>
    <p>{srs.sections['introduction']['scope']}</p>
    
    <h3>1.3 Definitions</h3>
    <ul>
        {''.join(f'<li>{defn}</li>' for defn in srs.sections['introduction']['definitions'])}
    </ul>
    
    <h2>2. Overall Description</h2>
    <h3>2.1 Product Functions</h3>
    <ul>
        {''.join(f'<li>{func}</li>' for func in srs.sections['overall_description']['product_functions'])}
    </ul>
    
    <h3>2.2 User Characteristics</h3>
    <ul>
        {''.join(f'<li>{user}</li>' for user in srs.sections['overall_description']['user_characteristics'])}
    </ul>
    
    <h3>2.3 Constraints</h3>
    <ul>
        {''.join(f'<li>{constraint}</li>' for constraint in srs.sections['overall_description']['constraints'])}
    </ul>
    
    <h2>3. Note</h2>
    <p><em>This is an initial SRS document generated by Module 1. It contains only the Introduction and Overall Description sections. 
    Specific Requirements and other detailed sections will be generated in subsequent modules of the requirements engineering system.</em></p>
</body>
</html>
"""
        return html

def main():
    """Test the SRS generator for Module 1 (Introduction and Overall Description only)"""
    # Sample requirements data
    sample_requirements = [
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
            'ambiguities': []
        }
    ]
    
    # Generate initial SRS (Module 1 scope)
    generator = SRSGenerator()
    srs = generator.generate_srs(sample_requirements)
    
    # Export to files
    json_file = generator.export_to_json(srs)
    html_file = generator.export_to_html(srs)
    
    print(f"Initial SRS generated successfully (Module 1 scope)!")
    print(f"Contains: Introduction and Overall Description sections only")
    print(f"JSON file: {json_file}")
    print(f"HTML file: {html_file}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Model-driven SRS Generator
==========================

Generates IEEE 830-style SRS sections using a text-generation model (Flan-T5).
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
import re

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Mock SRSDocument if srs_generator.py is unavailable
@dataclass
class SRSDocument:
    document_id: str
    title: str
    version: str
    date: str
    author: str
    sections: Dict[str, Any]


@dataclass
class ModelConfig:
    flan_model_name: str = "google/flan-t5-base"
    max_input_length: int = 512
    max_output_length: int = 256
    num_beams: int = 4
    temperature: float = 0.7
    do_sample: bool = True
    top_p: float = 0.9


class SRSModelGenerator:
    """Generates SRS sections using a generative model (Flan-T5)."""

    def __init__(self, config: Optional[ModelConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or ModelConfig()
        self.tokenizer: Optional[T5Tokenizer] = None
        self.model: Optional[T5ForConditionalGeneration] = None
        self._load_model()

    def _load_model(self):
        try:
            self.logger.info(f"Loading Flan-T5 model: {self.config.flan_model_name}")
            self.tokenizer = T5Tokenizer.from_pretrained(self.config.flan_model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.config.flan_model_name)
            self.logger.info("Flan-T5 loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise

    def _generate_text(self, prompt: str, max_length: int = 256) -> str:
        """Generate plain text response from the model."""
        assert self.tokenizer is not None and self.model is not None
        
        inputs = self.tokenizer.encode(
            prompt,
            return_tensors="pt",
            max_length=self.config.max_input_length,
            truncation=True,
        )

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                num_beams=self.config.num_beams,
                early_stopping=True,
                temperature=self.config.temperature,
                do_sample=self.config.do_sample,
                top_p=self.config.top_p,
                repetition_penalty=1.2,
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    def _extract_requirements_text(self, requirements_data: List[Dict[str, Any]]) -> str:
        """Extract and combine requirements text."""
        texts: List[str] = []
        for item in requirements_data:
            original = item.get('original_text') or item.get('content') or ''
            if original:
                texts.append(original.strip())
        return " ".join(texts)[:1000]

    def _generate_purpose(self, requirements_text: str) -> str:
        """Generate the purpose section."""
        prompt = f"""Write a brief purpose statement for a software requirements specification based on these requirements:

{requirements_text}

Purpose statement:"""
        
        result = self._generate_text(prompt, max_length=150)
        return result if result else "Define the purpose of the software system."

    def _generate_scope(self, requirements_text: str) -> str:
        """Generate the scope section."""
        prompt = f"""Write a scope description for a software system based on these requirements:

{requirements_text}

Scope:"""
        
        result = self._generate_text(prompt, max_length=200)
        return result if result else "Define the scope of the software system."

    def _generate_overview(self, requirements_text: str) -> str:
        """Generate the overview section."""
        prompt = f"""Write a brief overview of a software system based on these requirements:

{requirements_text}

Overview:"""
        
        result = self._generate_text(prompt, max_length=200)
        return result if result else "This document provides a comprehensive overview of the system requirements."

    def _generate_product_perspective(self, requirements_text: str) -> str:
        """Generate product perspective."""
        prompt = f"""Describe the product perspective and context for this system:

{requirements_text}

Product perspective:"""
        
        result = self._generate_text(prompt, max_length=200)
        return result if result else "The system operates as a standalone application."

    def _extract_functions(self, requirements_text: str) -> List[str]:
        """Extract main functions from requirements."""
        prompt = f"""List the main functions of this system (one per line):

{requirements_text}

Functions:"""
        
        result = self._generate_text(prompt, max_length=200)
        
        # Parse line-by-line
        functions = [line.strip() for line in result.split('\n') if line.strip()]
        # Remove numbered prefixes like "1.", "2.", etc.
        functions = [re.sub(r'^\d+[\.\)]\s*', '', f) for f in functions]
        # Remove bullet points
        functions = [re.sub(r'^[-•*]\s*', '', f) for f in functions]
        
        return functions[:5] if functions else ["User management", "Data processing"]

    def _extract_constraints(self, requirements_text: str) -> List[str]:
        """Extract system constraints."""
        prompt = f"""List the main constraints and limitations for this system:

{requirements_text}

Constraints:"""
        
        result = self._generate_text(prompt, max_length=150)
        
        constraints = [line.strip() for line in result.split('\n') if line.strip()]
        constraints = [re.sub(r'^\d+[\.\)]\s*', '', c) for c in constraints]
        constraints = [re.sub(r'^[-•*]\s*', '', c) for c in constraints]
        
        return constraints[:5] if constraints else ["Performance requirements", "Security requirements"]

    def _extract_definitions(self, requirements_text: str) -> List[str]:
        """Extract key terms and definitions."""
        # Simple heuristic: extract capitalized phrases and technical terms
        words = requirements_text.split()
        definitions = []
        
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3 and i > 0:
                # Check if it's not sentence start
                prev = words[i-1]
                if not prev.endswith('.'):
                    clean_word = re.sub(r'[^\w\s]', '', word)
                    if clean_word and clean_word not in definitions:
                        definitions.append(clean_word)
        
        return definitions[:10] if definitions else []

    def _generate_sections(self, requirements_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate all SRS sections using multiple targeted prompts."""
        requirements_text = self._extract_requirements_text(requirements_data)
        
        if not requirements_text:
            self.logger.warning("No requirements text available for generation")
            return self._empty_sections()
        
        self.logger.info("Generating SRS sections...")
        
        try:
            # Generate each section separately
            purpose = self._generate_purpose(requirements_text)
            scope = self._generate_scope(requirements_text)
            overview = self._generate_overview(requirements_text)
            product_perspective = self._generate_product_perspective(requirements_text)
            product_functions = self._extract_functions(requirements_text)
            constraints = self._extract_constraints(requirements_text)
            definitions = self._extract_definitions(requirements_text)
            
            return {
                "introduction": {
                    "purpose": purpose,
                    "scope": scope,
                    "definitions": definitions,
                    "references": [],
                    "overview": overview
                },
                "overall_description": {
                    "product_perspective": product_perspective,
                    "product_functions": product_functions,
                    "user_characteristics": ["End users", "System administrators"],
                    "constraints": constraints,
                    "assumptions": ["Users have basic technical knowledge", "System has internet connectivity"],
                    "dependencies": ["External APIs", "Database system"]
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating sections: {e}")
            return self._empty_sections()

    def _empty_sections(self) -> Dict[str, Any]:
        return {
            "introduction": {
                "purpose": "This document specifies the software requirements for the system.",
                "scope": "The system provides core functionality for the intended use case.",
                "definitions": [],
                "references": [],
                "overview": "This SRS document provides a comprehensive overview of system requirements."
            },
            "overall_description": {
                "product_perspective": "The system operates as a standalone application.",
                "product_functions": ["Core system functionality", "User interface"],
                "user_characteristics": ["End users", "System administrators"],
                "constraints": ["Performance requirements", "Security requirements"],
                "assumptions": ["Users have basic technical knowledge"],
                "dependencies": ["External systems and APIs"]
            }
        }

    def generate_srs(self, requirements_data: List[Dict[str, Any]], project_info: Optional[Dict[str, str]] = None) -> SRSDocument:
        if project_info is None:
            project_info = {
                'title': 'Software Requirements Specification',
                'author': 'Model-based Generator',
                'version': '1.0'
            }

        if not requirements_data:
            self.logger.warning("No requirements data provided")
            requirements_data = [{"original_text": "No requirements provided"}]

        document_id = f"SRS-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        sections = self._generate_sections(requirements_data)

        return SRSDocument(
            document_id=document_id,
            title=project_info.get('title', 'Software Requirements Specification'),
            version=project_info.get('version', '1.0'),
            date=datetime.now().strftime('%Y-%m-%d'),
            author=project_info.get('author', 'Model-based Generator'),
            sections=sections,
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example usage
    generator = SRSModelGenerator()
    requirements = [
        {
            "original_text": "The system should allow users to register, log in, and manage their profiles.",
            "extracted_fields": {"priority": "high", "type": "functional"}
        },
        {
            "original_text": "Admins must be able to manage user permissions and system configurations.",
            "extracted_fields": {"priority": "high", "type": "functional"}
        },
        {
            "original_text": "The system must support 1000 concurrent users with 99.9% uptime.",
            "extracted_fields": {"priority": "high", "type": "non-functional"}
        }
    ]
    
    project_info = {
        'title': 'User Management System SRS',
        'author': 'Engineering Team',
        'version': '1.0'
    }
    
    print("Generating SRS document...")
    doc = generator.generate_srs(requirements, project_info)
    
    print("\n" + "="*60)
    print(f"Document ID: {doc.document_id}")
    print(f"Title: {doc.title}")
    print(f"Version: {doc.version}")
    print(f"Date: {doc.date}")
    print(f"Author: {doc.author}")
    print("="*60)
    print("\nGenerated Sections:")
    print(json.dumps(doc.sections, indent=2, ensure_ascii=False))
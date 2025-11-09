#!/usr/bin/env python3
"""
Flask API Backend for Requirements Engineering System
====================================================

This module provides REST API endpoints for the React frontend to interact
with the requirements processing system.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
import logging
import re

# Import our existing modules
from main_orchestrator import RequirementsOrchestrator
from srs_generator import SRSGenerator
from json_to_srs_pdf import load_srs_from_json, render_html, save_pdf_or_html
from srs_model_generator import SRSModelGenerator
from srs_model_generator import SRSModelGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize orchestrator
orchestrator = RequirementsOrchestrator()
# Ensure audio transcription is enabled for the API unless explicitly disabled elsewhere
try:
    orchestrator.processor.config.enable_whisper = True
except Exception:
    pass

def validate_text_content(text: str) -> dict:
    """
    Validate text content against requirements:
    - Minimum 50 words required
    
    Returns:
        dict with 'valid' (bool) and 'errors' (list of error messages)
    """
    errors = []
    
    if not text or not text.strip():
        return {'valid': False, 'errors': ['Text content is empty']}
    
    # Require at least one alphabetic character (allow numbers/symbols but not only them)
    if not re.search(r'[A-Za-z]', text):
        errors.append('Text must include at least one alphabetic character (A-Z).')
    # Check minimum word count (50 words)
    words = text.strip().split()
    word_count = len([word for word in words if word])
    if word_count < 50:
        errors.append(f'Minimum 50 words required (current: {word_count} words)')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Requirements Engineering API'
    })

@app.route('/api/process-single', methods=['POST'])
def process_single_requirement():
    """Process a single requirement from text input"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        input_type = data.get('type', 'text')
        content = data.get('content', '')
        project_info = data.get('project_info', {})
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Validate content
        validation = validate_text_content(content)
        if not validation['valid']:
            return jsonify({'error': 'Text content validation failed', 'validation_errors': validation['errors']}), 400

        # Prepare input data
        if input_type == 'text':
            input_data = {'type': 'text', 'content': content}
        else:
            return jsonify({'error': 'Unsupported input type'}), 400
        
        # Process the requirement
        result = orchestrator.process_single_requirement(input_data)
        
        # Add project info to result
        result['project_info'] = project_info
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing single requirement: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-audio', methods=['POST'])
def process_audio_requirement():
    """Process a single requirement from audio recording"""
    try:
        audio_file = request.files.get('audio')
        project_info_str = request.form.get('project_info', '{}')
        
        if not audio_file:
            return jsonify({'error': 'No audio file provided'}), 400
        
        project_info = json.loads(project_info_str)
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Process the audio requirement
            input_data = {'type': 'audio', 'file_path': temp_file_path}
            result = orchestrator.process_single_requirement(input_data)

            # If processing failed (e.g., whisper disabled or other error), return 400
            if result.get('status') == 'failed':
                return jsonify({'error': result.get('error', 'Audio processing failed')}), 400
            
            # Validate the transcribed text
            if result.get('status') == 'completed':
                transcribed_text = result.get('original_text', '')
                validation_result = validate_text_content(transcribed_text)
                
                if not validation_result['valid']:
                    return jsonify({
                        'error': 'Audio content validation failed',
                        'validation_errors': validation_result['errors'],
                        'transcribed_text': transcribed_text
                    }), 400
            
            # Add project info to result
            result['project_info'] = project_info
            result['source_type'] = 'audio_recording'
            
            return jsonify(result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        logger.error(f"Error processing audio requirement: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/process-batch', methods=['POST'])
def process_batch_requirements():
    """Process multiple requirements from uploaded files"""
    try:
        files = request.files.getlist('files')
        project_info_str = request.form.get('project_info', '{}')
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        project_info = json.loads(project_info_str)
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            results = []
            validation_errors_list = []
            
            for file in files:
                if file.filename == '':
                    continue
                
                # Save file to temp directory
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                
                # Determine input type and read content for validation
                if file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
                    input_data = {'type': 'audio', 'file_path': file_path}
                    # Process first to get transcription
                    result = orchestrator.process_single_requirement(input_data)
                    content_to_validate = result.get('original_text', '')
                else:
                    # Read text file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content_to_validate = content
                    input_data = {'type': 'text', 'content': content}
                    # Process the requirement
                    result = orchestrator.process_single_requirement(input_data)
                
                # Validate the content
                validation_result = validate_text_content(content_to_validate)
                
                if not validation_result['valid']:
                    validation_errors_list.append({
                        'file': file.filename,
                        'errors': validation_result['errors']
                    })
                
                result['source_file'] = file.filename
                result['validation'] = validation_result
                results.append(result)
            
            # If any validation errors, return them
            if validation_errors_list:
                return jsonify({
                    'error': 'File content validation failed',
                    'validation_errors': validation_errors_list,
                    'details': 'One or more files do not meet the requirements'
                }), 400
            
            # Add project info to results
            batch_result = {
                'results': results,
                'project_info': project_info,
                'timestamp': datetime.now().isoformat(),
                'total_files': len(results),
                'status': 'completed'
            }
            
            return jsonify(batch_result)
        
    except Exception as e:
        logger.error(f"Error processing batch requirements: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-srs', methods=['POST'])
def generate_srs():
    """Generate SRS document from processed results"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        results = data.get('results')
        project_info = data.get('project_info', {})
        
        if not results:
            return jsonify({'error': 'No results provided'}), 400
        
        # Ensure results is a list
        if not isinstance(results, list):
            results = [results]
        
        # Generate SRS content using the model-based generator
        model_gen = SRSModelGenerator()
        srs = model_gen.generate_srs(results, project_info)
        
        # Convert SRS to dictionary for JSON response
        srs_dict = {
            'document_id': srs.document_id,
            'title': srs.title,
            'version': srs.version,
            'date': srs.date,
            'author': srs.author,
            'sections': srs.sections
        }
        
        return jsonify(srs_dict)
        
    except Exception as e:
        logger.error(f"Error generating SRS: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-srs/<format>', methods=['POST'])
def download_srs(format):
    """Download SRS document in specified format"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        srs_data = data.get('srs_data')
        
        if not srs_data:
            return jsonify({'error': 'No SRS data provided'}), 400
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == 'json':
            filename = f"srs_{timestamp}.json"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(srs_data, f, indent=2, ensure_ascii=False)
                temp_file = f.name
        elif format.lower() == 'html':
            filename = f"srs_{timestamp}.html"
            # Generate HTML content
            html_content = generate_html_content(srs_data)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
        else:
            return jsonify({'error': 'Unsupported format'}), 400
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading SRS: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-srs-pdf', methods=['POST'])
def generate_srs_pdf():
    """Generate SRS PDF (or HTML fallback) directly from posted JSON and return the file."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # If caller sent 'results', generate SRS via model first
        def _is_empty_sections(sec: dict) -> bool:
            if not isinstance(sec, dict):
                return True
            intro = sec.get('introduction') or {}
            overall = sec.get('overall_description') or {}
            has_intro = any(bool(str(intro.get(k, '')).strip()) for k in ['purpose','scope','overview']) or bool(intro.get('definitions'))
            has_overall = any(bool(overall.get(k)) for k in ['product_functions','user_characteristics','constraints','assumptions','dependencies']) or bool(str(overall.get('product_perspective','')).strip())
            return not (has_intro or has_overall)

        sections = data.get('sections') or data.get('srs_sections')
        if ((not sections) or _is_empty_sections(sections)) and data.get('results'):
            model_gen = SRSModelGenerator()
            project_info = data.get('project_info', {})
            srs = model_gen.generate_srs(data['results'], project_info)
            html = render_html({
                'document_id': srs.document_id,
                'title': srs.title,
                'version': srs.version,
                'date': srs.date,
                'author': srs.author,
                'sections': srs.sections,
            })
            out_path = save_pdf_or_html(html, f"srs_{srs.document_id}.pdf")
            return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))

        # Else load SRS directly from provided JSON (accepts 'sections' or 'srs_sections')
        import tempfile, os, json as _json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            _json.dump(data, f, ensure_ascii=False)
            temp_json = f.name

        try:
            srs_doc = load_srs_from_json(temp_json)
            html = render_html(srs_doc)
            out_path = save_pdf_or_html(html, f"srs_{srs_doc.document_id}.pdf")
            return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
        finally:
            try:
                os.unlink(temp_json)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Error generating SRS PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_html_content(srs_data):
    """Generate HTML content for SRS document.
    Accepts either srs_data['sections'] or srs_data['srs_sections'].
    """
    sections = srs_data.get('sections') or srs_data.get('srs_sections') or {}
    intro = sections.get('introduction', {})
    overall = sections.get('overall_description', {})
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{srs_data['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; margin-top: 20px; }}
        .metadata {{ background-color: #ecf0f1; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        ul {{ margin: 10px 0; }}
        li {{ margin: 5px 0; }}
        .section {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{srs_data['title']}</h1>
    
    <div class="metadata">
        <p><strong>Document ID:</strong> {srs_data['document_id']}</p>
        <p><strong>Version:</strong> {srs_data['version']}</p>
        <p><strong>Date:</strong> {srs_data['date']}</p>
        <p><strong>Author:</strong> {srs_data['author']}</p>
    </div>
    
    <div class="section">
        <h2>1. Introduction</h2>
        <h3>1.1 Purpose</h3>
        <p>{intro.get('purpose','')}</p>
        
        <h3>1.2 Scope</h3>
        <p>{intro.get('scope','')}</p>
        
        <h3>1.3 Definitions</h3>
        <ul>
            {''.join(f'<li>{defn}</li>' for defn in intro.get('definitions', []))}
        </ul>
        
        <h3>1.4 Overview</h3>
        <p>{intro.get('overview','')}</p>
    </div>
    
    <div class="section">
        <h2>2. Overall Description</h2>
        <h3>2.1 Product Functions</h3>
        <ul>
            {''.join(f'<li>{func}</li>' for func in overall.get('product_functions', []))}
        </ul>
        
        <h3>2.2 User Characteristics</h3>
        <ul>
            {''.join(f'<li>{user}</li>' for user in overall.get('user_characteristics', []))}
        </ul>
        
        <h3>2.3 Constraints</h3>
        <ul>
            {''.join(f'<li>{constraint}</li>' for constraint in overall.get('constraints', []))}
        </ul>
        
        <h3>2.4 Assumptions</h3>
        <ul>
            {''.join(f'<li>{assumption}</li>' for assumption in (overall.get('assumptions', []) if isinstance(overall.get('assumptions'), list) else [overall.get('assumptions')] if overall.get('assumptions') else []))}
        </ul>
        
        <h3>2.5 Dependencies</h3>
        <ul>
            {''.join(f'<li>{dep}</li>' for dep in overall.get('dependencies', []))}
        </ul>
    </div>
    
    <div class="section">
        <h2>3. Note</h2>
        <p><em>This is an initial SRS document generated by Module 1. It contains only the Introduction and Overall Description sections. 
        Specific Requirements and other detailed sections will be generated in subsequent modules of the requirements engineering system.</em></p>
    </div>
</body>
</html>"""

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        stats = orchestrator.get_system_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_system():
    """Clean up old data"""
    try:
        data = request.get_json() or {}
        days_old = data.get('days_old', 30)
        
        orchestrator.cleanup_system(days_old)
        
        return jsonify({
            'message': f'System cleanup completed (removed data older than {days_old} days)',
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Requirements Engineering API Server...")
    print("API Endpoints:")
    print("  GET  /api/health - Health check")
    print("  POST /api/process-single - Process single requirement")
    print("  POST /api/process-audio - Process audio recording")
    print("  POST /api/process-batch - Process batch requirements")
    print("  POST /api/generate-srs - Generate SRS document")
    print("  POST /api/download-srs/<format> - Download SRS")
    print("  GET  /api/stats - Get system statistics")
    print("  POST /api/cleanup - Clean up system")
    print("\nServer running on http://localhost:8000")
    
    app.run(host='0.0.0.0', port=8000, debug=True)

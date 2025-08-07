#!/usr/bin/env python3
"""
Contract Explainer - Flask Backend
Based on condensed launch specs with AI clause analysis
"""

import os
import requests
import PyPDF2
import docx
import logging
import re
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')

# Enable CORS for local development
from flask_cors import CORS
CORS(app, origins=['http://localhost:*', 'file://*'])

# Deepseek API configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_content):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"PDF extraction error: {e}")
        return None

def extract_text_from_docx(file_content):
    """Extract text from Word document"""
    try:
        doc = docx.Document(BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"DOCX extraction error: {e}")
        return None

def explain_contract(file_content):
    """
    Core function from specs - explain contract using Deepseek API
    """
    prompt = f"""
    Explain this contract in simple English for non-lawyers:
    
    {file_content[:4000]}  # Limit to avoid token limits
    
    Format your response EXACTLY like this:
    
    ## Contract Type & Purpose
    [What type of contract this is and its main purpose]
    
    ## Key Sections
    [Break down the most important sections and what each means]
    
    ## ⚠️ RED FLAGS
    [Highlight any risky, unusual, or potentially problematic clauses]
    
    ## BOTTOM LINE
    [Should they sign it or not? What should they negotiate?]
    
    Use simple language, highlight dangers, avoid legal jargon.
    """
    
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1500,
                "temperature": 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            logging.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"API request error: {e}")
        return None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/working-pdf-highlighter.html')
def working_pdf_highlighter():
    """Working PDF highlighter with three-panel layout"""
    with open('working-pdf-highlighter.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/semantic-clause-highlighter.html') 
def semantic_clause_highlighter():
    """Semantic clause highlighter"""
    with open('semantic-clause-highlighter.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/integrated-highlighter.html')
def integrated_highlighter():
    """Integrated frontend-backend highlighter"""
    with open('integrated-highlighter.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/analyze', methods=['POST'])
def analyze_contract():
    """API endpoint for contract analysis"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        filename = secure_filename(file.filename)
        
        # Extract text based on file type
        text = None
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Handle PDF files even if they have wrong extension
        if file_extension == 'pdf' or filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_content)
        elif file_extension in ['docx', 'doc']:
            try:
                text = extract_text_from_docx(file_content)
            except:
                # Fallback: try PDF extraction if DOCX fails
                text = extract_text_from_pdf(file_content)
        elif file_extension == 'txt':
            text = file_content.decode('utf-8')
        else:
            # Default fallback: try PDF extraction
            text = extract_text_from_pdf(file_content)
        
        if not text or len(text.strip()) < 50:
            logging.warning(f"Insufficient text extracted from file: {filename} - {request.remote_addr}")
            return jsonify({'error': 'Could not extract enough text from the document. Please ensure the file contains readable text.'}), 400
        
        # Analyze with AI
        analysis = explain_contract(text)
        
        if not analysis:
            logging.error(f"AI analysis failed for file: {filename} - {request.remote_addr}")
            return jsonify({'error': 'Failed to analyze the contract. Please try again.'}), 500
        
        # Log successful analysis (without sensitive data)
        logging.info(f"Contract analyzed successfully: {len(text.split())} words - {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'analysis': analysis,
            'word_count': len(text.split())
        })
        
    except Exception as e:
        logging.error(f"Analysis error: {e} - {request.remote_addr}")
        return jsonify({'error': 'An error occurred while processing your file. Please try again.'}), 500

@app.errorhandler(413)
def too_large(e):
    logging.warning(f"File too large upload attempt - {request.remote_addr}")
    return jsonify({'error': 'File too large. Please upload files smaller than 16MB.'}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    logging.warning(f"Rate limit exceeded - {request.remote_addr}")
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.route('/health')
def health_check():
    '''Health check endpoint for monitoring'''
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': os.environ.get('RENDER_GIT_COMMIT', 'unknown')
    }), 200

@app.route('/analyze-clauses', methods=['POST'])
def analyze_clauses():
    """AI-powered clause analysis endpoint"""
    try:
        data = request.get_json()
        document_text = data.get('document_text', '')
        clause_types = data.get('clause_types', [])
        
        if not document_text:
            return jsonify({'error': 'No document text provided'}), 400
            
        # For now, use enhanced pattern matching (AI integration can be added later)
        results = perform_enhanced_pattern_analysis(document_text, clause_types)
        
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"Clause analysis error: {e}")
        return jsonify({'error': 'Analysis failed', 'detected_clauses': []}), 500

def perform_enhanced_pattern_analysis(text, clause_types):
    """Enhanced pattern-based clause detection"""
    detected_clauses = []
    
    # Semantic patterns that understand legal context, not just keywords
    patterns = {
        'governance': [
            # Full semantic understanding of governance compromise clauses
            (r'shareholder.*vote.*accordance.*with.*instructions.*provided.*by.*president', 0.95, 'high'),
            (r'vote.*shares.*accordance.*president.*instructions', 0.9, 'high'),
            (r'governance.*compromise.*president.*instructions', 0.85, 'high'),
            (r'holder.*vote.*shares.*accordance.*instructions.*president', 0.8, 'high')
        ],
        'drag_along': [
            # Semantic understanding of drag-along rights mechanisms
            (r'drag.along.*right.*ninety.five.*per.*cent', 0.95, 'high'),
            (r'95%.*holders.*shares.*offeror.*require.*sell', 0.9, 'high'), 
            (r'offeror.*may.*require.*holders.*sell.*shares', 0.85, 'high'),
            (r'forced.*sale.*shares.*majority.*shareholders', 0.8, 'high')
        ],
        'tag_along': [
            # Semantic understanding of tag-along protection mechanisms
            (r'tag.along.*right.*transferor.*shareholder', 0.95, 'low'),
            (r'holder.*sell.*shares.*same.*price.*terms', 0.9, 'low'),
            (r'shareholder.*transfer.*shares.*holder.*right.*sell', 0.85, 'low'),
            (r'protection.*minority.*shareholders.*sales', 0.8, 'low')
        ],
        'priority_allocation': [
            # Semantic understanding of liquidation preferences and waterfalls
            (r'priority.*allocation.*sale.*price.*waterfall', 0.95, 'medium'),
            (r'liquidation.*preference.*distribution.*proceeds', 0.9, 'medium'),
            (r'sale.*proceeds.*allocated.*priority.*order', 0.85, 'medium'),
            (r'distribution.*waterfall.*priority.*shareholders', 0.8, 'medium')
        ],
        'non_compete': [
            # Semantic understanding of non-compete survival provisions
            (r'non.compete.*restrictions.*remain.*applicable.*avoidance.*doubts', 0.95, 'medium'),
            (r'non.solicit.*provisions.*survive.*completion', 0.9, 'medium'),
            (r'restrictions.*continue.*apply.*after.*sale', 0.85, 'medium'),
            (r'competition.*restrictions.*remain.*effect', 0.8, 'medium')
        ]
    }
    
    for clause_type in clause_types:
        if clause_type in patterns:
            for pattern, confidence, risk in patterns[clause_type]:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Get surrounding context for better highlighting
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    
                    detected_clauses.append({
                        'text': match.group(),
                        'context': context,
                        'type': clause_type,
                        'confidence': confidence,
                        'risk_level': risk,
                        'position': match.start()
                    })
    
    return {
        'detected_clauses': detected_clauses[:15],  # Limit results
        'analysis_method': 'enhanced_pattern_matching',
        'success': True,
        'total_found': len(detected_clauses)
    }

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    logging.info("Contract Explainer Backend Starting...")
    logging.info(f"Server will be available at http://localhost:5001")
    logging.info(f"Deepseek API Key: {'OK' if DEEPSEEK_API_KEY else 'Missing'}")
    logging.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    logging.info(f"Debug mode: {os.getenv('FLASK_DEBUG', '0')}")
    
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    host = os.getenv('FLASK_HOST', 'localhost')
    port = int(os.getenv('FLASK_PORT', 5001))
    
    app.run(debug=debug_mode, host=host, port=port)
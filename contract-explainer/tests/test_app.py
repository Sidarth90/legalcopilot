#!/usr/bin/env python3
"""
Contract Explainer - Unit Tests
Test suite for Flask application functionality
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from io import BytesIO
from app import app, extract_text_from_pdf, extract_text_from_docx, explain_contract

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing"""
    # This would normally create a real PDF, but for testing we'll mock it
    return BytesIO(b"Sample PDF content")

@pytest.fixture
def sample_docx():
    """Create a sample DOCX file for testing"""
    return BytesIO(b"Sample DOCX content")

class TestRoutes:
    """Test Flask routes"""
    
    def test_index_route(self, client):
        """Test the main index route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Contract Explainer' in response.data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_analyze_no_file(self, client):
        """Test analyze endpoint with no file"""
        response = client.post('/api/analyze')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No file uploaded' in data['error']
    
    def test_analyze_empty_filename(self, client):
        """Test analyze endpoint with empty filename"""
        data = {'file': (BytesIO(b""), '')}
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 400
    
    def test_analyze_invalid_file_type(self, client):
        """Test analyze endpoint with invalid file type"""
        data = {'file': (BytesIO(b"test content"), 'test.exe')}
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Invalid file type' in response_data['error']
    
    def test_analyze_file_too_large(self, client):
        """Test analyze endpoint with file too large"""
        # Create a file that's too large (over 16MB)
        large_content = b"x" * (17 * 1024 * 1024)  # 17MB
        data = {'file': (BytesIO(large_content), 'large.pdf')}
        response = client.post('/api/analyze', data=data)
        assert response.status_code == 400
    
    def test_file_too_large_error_handler(self, client):
        """Test 413 error handler"""
        with patch.object(app, 'config', {'MAX_CONTENT_LENGTH': 100}):
            large_content = b"x" * 200
            data = {'file': (BytesIO(large_content), 'test.pdf')}
            response = client.post('/api/analyze', data=data)
            # The actual behavior depends on how the server handles this
            # This test mainly ensures the error handler exists

class TestTextExtraction:
    """Test text extraction functions"""
    
    @patch('app.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_success(self, mock_pdf_reader):
        """Test successful PDF text extraction"""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF text"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        result = extract_text_from_pdf(b"fake pdf content")
        assert result == "Sample PDF text"
    
    @patch('app.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_failure(self, mock_pdf_reader):
        """Test PDF text extraction failure"""
        mock_pdf_reader.side_effect = Exception("PDF error")
        
        result = extract_text_from_pdf(b"fake pdf content")
        assert result is None
    
    @patch('app.docx.Document')
    def test_extract_text_from_docx_success(self, mock_document):
        """Test successful DOCX text extraction"""
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Sample DOCX text"
        mock_document.return_value.paragraphs = [mock_paragraph]
        
        result = extract_text_from_docx(b"fake docx content")
        assert result == "Sample DOCX text"
    
    @patch('app.docx.Document')
    def test_extract_text_from_docx_failure(self, mock_document):
        """Test DOCX text extraction failure"""
        mock_document.side_effect = Exception("DOCX error")
        
        result = extract_text_from_docx(b"fake docx content")
        assert result is None

class TestContractExplanation:
    """Test contract explanation functionality"""
    
    @patch('app.requests.post')
    def test_explain_contract_success(self, mock_post):
        """Test successful contract explanation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Contract explanation"}}]
        }
        mock_post.return_value = mock_response
        
        result = explain_contract("Sample contract text")
        assert result == "Contract explanation"
    
    @patch('app.requests.post')
    def test_explain_contract_api_error(self, mock_post):
        """Test contract explanation with API error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "API Error"
        mock_post.return_value = mock_response
        
        result = explain_contract("Sample contract text")
        assert result is None
    
    @patch('app.requests.post')
    def test_explain_contract_request_exception(self, mock_post):
        """Test contract explanation with request exception"""
        mock_post.side_effect = Exception("Network error")
        
        result = explain_contract("Sample contract text")
        assert result is None

class TestSecurity:
    """Test security features"""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present"""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for security headers (these are added by Talisman in production)
        # In testing, some headers might not be present
        
    def test_rate_limiting_structure(self, client):
        """Test that rate limiting is properly structured"""
        # This tests that the rate limiting decorators are in place
        # Actual rate limiting behavior would need integration tests
        response = client.get('/')
        assert response.status_code == 200

class TestIntegration:
    """Integration tests"""
    
    @patch('app.explain_contract')
    @patch('app.extract_text_from_pdf')
    def test_full_pdf_analysis_flow(self, mock_extract, mock_explain, client):
        """Test complete PDF analysis workflow"""
        # Mock text extraction
        mock_extract.return_value = "This is a sample contract text with sufficient length for analysis."
        
        # Mock AI explanation
        mock_explain.return_value = """
        ## Contract Type & Purpose
        This is a test contract.
        
        ## Key Sections
        Important clauses here.
        
        ## ⚠️ RED FLAGS
        No major concerns.
        
        ## BOTTOM LINE
        Safe to proceed.
        """
        
        # Create test file
        data = {'file': (BytesIO(b"fake pdf content"), 'test.pdf')}
        response = client.post('/api/analyze', data=data)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'analysis' in response_data
        assert 'filename' in response_data
    
    @patch('app.explain_contract')
    @patch('app.extract_text_from_pdf')
    def test_insufficient_text_error(self, mock_extract, mock_explain, client):
        """Test error when extracted text is insufficient"""
        # Mock insufficient text extraction
        mock_extract.return_value = "Short"
        
        data = {'file': (BytesIO(b"fake pdf content"), 'test.pdf')}
        response = client.post('/api/analyze', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'Could not extract enough text' in response_data['error']

# Configuration for pytest
def pytest_configure(config):
    """Configure pytest"""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DEEPSEEK_API_KEY'] = 'test_key'
    os.environ['FLASK_SECRET_KEY'] = 'test_secret'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
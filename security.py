"""
Contract Explainer - Security Configuration
Production-ready security enhancements for Flask application
"""

import os
import logging
from functools import wraps
from flask import request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import redis
from werkzeug.middleware.proxy_fix import ProxyFix

class SecurityManager:
    """Centralized security management for the application"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security features for Flask app"""
        self.app = app
        
        # Configure logging
        self.setup_logging()
        
        # Initialize Sentry for error tracking
        self.setup_sentry()
        
        # Configure CORS
        self.setup_cors()
        
        # Setup rate limiting
        self.setup_rate_limiting()
        
        # Configure security headers
        self.setup_security_headers()
        
        # Setup proxy handling for production
        self.setup_proxy_handling()
        
        # Setup request validation
        self.setup_request_validation()
    
    def setup_logging(self):
        """Configure structured logging"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('app.log') if os.getenv('FLASK_ENV') == 'development' else logging.NullHandler()
            ]
        )
        
        # Suppress werkzeug logs in production
        if os.getenv('FLASK_ENV') == 'production':
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
    
    def setup_sentry(self):
        """Initialize Sentry error tracking"""
        sentry_dsn = os.getenv('SENTRY_DSN')
        
        if sentry_dsn:
            sentry_logging = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    FlaskIntegration(),
                    sentry_logging
                ],
                traces_sample_rate=0.1,  # Capture 10% of transactions for performance monitoring
                profiles_sample_rate=0.1,  # Capture 10% of the transactions for profiling
                environment=os.getenv('FLASK_ENV', 'production')
            )
            
            logging.info("Sentry error tracking initialized")
    
    def setup_cors(self):
        """Configure Cross-Origin Resource Sharing"""
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        
        if os.getenv('FLASK_ENV') == 'production':
            # Strict CORS in production
            CORS(self.app, 
                 origins=allowed_origins,
                 supports_credentials=False,
                 allow_headers=['Content-Type', 'Authorization'],
                 methods=['GET', 'POST', 'OPTIONS'])
        else:
            # Permissive CORS in development
            CORS(self.app)
        
        logging.info(f"CORS configured for origins: {allowed_origins}")
    
    def setup_rate_limiting(self):
        """Configure rate limiting"""
        # Try Redis first, fallback to memory
        redis_url = os.getenv('REDIS_URL', os.getenv('REDIS_PRIVATE_URL'))
        
        if redis_url:
            try:
                redis_client = redis.from_url(redis_url, decode_responses=True)
                redis_client.ping()  # Test connection
                storage_uri = redis_url
                logging.info("Using Redis for rate limiting")
            except:
                storage_uri = "memory://"
                logging.warning("Redis unavailable, using memory for rate limiting")
        else:
            storage_uri = "memory://"
            logging.info("Using memory for rate limiting")
        
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            storage_uri=storage_uri,
            default_limits=["1000 per hour"]
        )
        
        # Add custom rate limit decorators
        self.api_limit = self.limiter.limit("30 per hour")  # Stricter for API
        self.upload_limit = self.limiter.limit("10 per hour")  # Very strict for uploads
    
    def setup_security_headers(self):
        """Configure security headers using Talisman"""
        # Content Security Policy
        csp = {
            'default-src': "'self'",
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Required for Tailwind and inline scripts
                'cdn.tailwindcss.com',
                'pagead2.googlesyndication.com',
                'www.googletagmanager.com'
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Required for Tailwind
                'cdn.tailwindcss.com'
            ],
            'img-src': [
                "'self'",
                'data:',
                'https:',
                'pagead2.googlesyndication.com'
            ],
            'font-src': [
                "'self'",
                'data:'
            ],
            'connect-src': [
                "'self'"
            ],
            'frame-src': [
                'pagead2.googlesyndication.com'
            ],
            'object-src': "'none'",
            'base-uri': "'self'"
        }
        
        # Initialize Talisman
        Talisman(
            self.app,
            force_https=os.getenv('FLASK_ENV') == 'production',
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,
            content_security_policy=csp,
            content_security_policy_nonce_in=['script-src'],
            feature_policy={
                'geolocation': "'none'",
                'microphone': "'none'",
                'camera': "'none'"
            }
        )
        
        logging.info("Security headers configured")
    
    def setup_proxy_handling(self):
        """Configure proxy handling for production deployments"""
        if os.getenv('FLASK_ENV') == 'production':
            self.app.wsgi_app = ProxyFix(
                self.app.wsgi_app,
                x_for=1,  # Number of proxies setting X-Forwarded-For
                x_proto=1,  # Number of proxies setting X-Forwarded-Proto  
                x_host=1,  # Number of proxies setting X-Forwarded-Host
                x_prefix=1  # Number of proxies setting X-Forwarded-Prefix
            )
    
    def setup_request_validation(self):
        """Setup request validation middleware"""
        
        @self.app.before_request
        def validate_request():
            """Validate incoming requests"""
            # Skip validation for health checks
            if request.endpoint == 'health_check':
                return
            
            # Validate Content-Type for POST requests
            if request.method == 'POST' and request.endpoint == 'analyze_contract':
                if 'multipart/form-data' not in request.content_type:
                    return jsonify({'error': 'Invalid Content-Type'}), 400
            
            # Log requests in development
            if os.getenv('FLASK_ENV') == 'development':
                logging.info(f"{request.method} {request.path} - {get_remote_address()}")
        
        @self.app.after_request
        def add_security_headers(response):
            """Add additional security headers"""
            # Remove server header
            response.headers.pop('Server', None)
            
            # Add custom headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Cache control for static assets
            if request.endpoint and 'static' in request.endpoint:
                response.headers['Cache-Control'] = 'public, max-age=31536000'
            else:
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            
            return response
    
    def file_security_check(self, file):
        """Enhanced file security validation"""
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check file extension
        allowed_extensions = {'pdf', 'docx', 'doc', 'txt'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return False, "Invalid file type"
        
        # Check file size (additional check beyond Flask config)
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > 16 * 1024 * 1024:  # 16MB
            return False, "File too large"
        
        if size < 100:  # Minimum file size
            return False, "File too small"
        
        # Check for suspicious patterns in filename
        suspicious_patterns = ['..', '/', '\\', '<', '>', '|', ':', '*', '?', '"']
        if any(pattern in file.filename for pattern in suspicious_patterns):
            return False, "Invalid filename"
        
        return True, "File validation passed"

def security_required(f):
    """Decorator for endpoints that require enhanced security"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Additional security checks can be added here
        return f(*args, **kwargs)
    return decorated_function

def api_key_required(f):
    """Decorator for API endpoints that require API key (future feature)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For future API key authentication
        return f(*args, **kwargs)
    return decorated_function
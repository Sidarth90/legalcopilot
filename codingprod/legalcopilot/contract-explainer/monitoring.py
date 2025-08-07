"""
Contract Explainer - Monitoring and Observability
Comprehensive monitoring, logging, and alerting setup
"""

import os
import time
import logging
import psutil
from functools import wraps
from flask import request, g, jsonify
from datetime import datetime, timedelta
import json

class ApplicationMonitor:
    """Application monitoring and metrics collection"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = {
            'requests_total': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'uploads_total': 0,
            'analysis_total': 0,
            'analysis_errors': 0,
            'response_times': [],
            'active_users': set(),
            'errors': []
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize monitoring for Flask app"""
        self.app = app
        
        # Setup request monitoring
        self.setup_request_monitoring()
        
        # Setup error handling
        self.setup_error_handling()
        
        # Setup metrics endpoint
        self.setup_metrics_endpoint()
    
    def setup_request_monitoring(self):
        """Setup request-level monitoring"""
        
        @self.app.before_request
        def start_timer():
            g.start_time = time.time()
            g.request_id = f"{int(time.time())}-{hash(request.remote_addr) % 10000}"
            
            # Track active users (by IP for privacy)
            self.metrics['active_users'].add(request.remote_addr)
            
            # Log request start
            logging.info(f"Request started: {g.request_id} - {request.method} {request.path}")
        
        @self.app.after_request
        def record_metrics(response):
            # Calculate response time
            response_time = time.time() - g.start_time
            self.metrics['response_times'].append(response_time)
            
            # Keep only last 1000 response times for memory efficiency
            if len(self.metrics['response_times']) > 1000:
                self.metrics['response_times'] = self.metrics['response_times'][-1000:]
            
            # Update counters
            self.metrics['requests_total'] += 1
            
            if response.status_code < 400:
                self.metrics['requests_successful'] += 1
            else:
                self.metrics['requests_failed'] += 1
            
            # Track specific endpoints
            if request.endpoint == 'analyze_contract':
                self.metrics['uploads_total'] += 1
                if response.status_code == 200:
                    self.metrics['analysis_total'] += 1
                else:
                    self.metrics['analysis_errors'] += 1
            
            # Log request completion
            logging.info(
                f"Request completed: {g.request_id} - "
                f"{response.status_code} - {response_time:.3f}s"
            )
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{response_time:.3f}s"
            response.headers['X-Request-ID'] = g.request_id
            
            return response
    
    def setup_error_handling(self):
        """Setup comprehensive error handling"""
        
        @self.app.errorhandler(Exception)
        def handle_exception(e):
            """Handle all unhandled exceptions"""
            error_info = {
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': getattr(g, 'request_id', 'unknown'),
                'error_type': type(e).__name__,
                'error_message': str(e),
                'request_method': request.method,
                'request_path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            }
            
            # Store error (keep only last 100 for memory)
            self.metrics['errors'].append(error_info)
            if len(self.metrics['errors']) > 100:
                self.metrics['errors'] = self.metrics['errors'][-100:]
            
            # Log error with full context
            logging.error(f"Unhandled exception: {json.dumps(error_info, indent=2)}")
            
            # Return user-friendly error response
            return jsonify({
                'error': 'An unexpected error occurred. Please try again.',
                'request_id': error_info['request_id']
            }), 500
        
        @self.app.errorhandler(404)
        def handle_not_found(e):
            logging.warning(f"404 Not Found: {request.path} - {request.remote_addr}")
            return jsonify({'error': 'Page not found'}), 404
        
        @self.app.errorhandler(500)
        def handle_server_error(e):
            logging.error(f"500 Server Error: {request.path} - {request.remote_addr}")
            return jsonify({'error': 'Server error. Please try again.'}), 500
    
    def setup_metrics_endpoint(self):
        """Setup metrics endpoint for monitoring"""
        
        @self.app.route('/metrics')
        def metrics():
            """Prometheus-compatible metrics endpoint"""
            system_metrics = self.get_system_metrics()
            app_metrics = self.get_application_metrics()
            
            # Simple text format for now (can be extended to Prometheus format)
            metrics_text = f"""
# Application Metrics
requests_total {app_metrics['requests_total']}
requests_successful {app_metrics['requests_successful']}
requests_failed {app_metrics['requests_failed']}
uploads_total {app_metrics['uploads_total']}
analysis_total {app_metrics['analysis_total']}
analysis_errors {app_metrics['analysis_errors']}
active_users {len(app_metrics['active_users'])}
avg_response_time {app_metrics['avg_response_time']:.3f}
error_count {len(app_metrics['errors'])}

# System Metrics
cpu_usage {system_metrics['cpu_percent']}
memory_usage {system_metrics['memory_percent']}
disk_usage {system_metrics['disk_percent']}
"""
            
            return metrics_text.strip(), 200, {'Content-Type': 'text/plain'}
        
        @self.app.route('/health/detailed')
        def detailed_health():
            """Detailed health check with system information"""
            system_metrics = self.get_system_metrics()
            app_metrics = self.get_application_metrics()
            
            # Determine health status
            health_status = 'healthy'
            issues = []
            
            # Check system resources
            if system_metrics['cpu_percent'] > 80:
                health_status = 'degraded'
                issues.append('High CPU usage')
            
            if system_metrics['memory_percent'] > 85:
                health_status = 'degraded'
                issues.append('High memory usage')
            
            if system_metrics['disk_percent'] > 90:
                health_status = 'degraded'
                issues.append('Low disk space')
            
            # Check error rate
            total_requests = app_metrics['requests_total']
            if total_requests > 0:
                error_rate = app_metrics['requests_failed'] / total_requests
                if error_rate > 0.1:  # 10% error rate
                    health_status = 'unhealthy'
                    issues.append('High error rate')
            
            # Check recent errors
            recent_errors = [
                e for e in app_metrics['errors']
                if datetime.fromisoformat(e['timestamp']) > 
                   datetime.utcnow() - timedelta(minutes=5)
            ]
            
            if len(recent_errors) > 10:  # More than 10 errors in 5 minutes
                health_status = 'degraded'
                issues.append('Frequent recent errors')
            
            return jsonify({
                'status': health_status,
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'issues': issues,
                'metrics': {
                    'system': system_metrics,
                    'application': {
                        k: v for k, v in app_metrics.items()
                        if k not in ['active_users', 'errors', 'response_times']
                    }
                },
                'uptime_seconds': time.time() - self.start_time
            })
    
    def get_system_metrics(self):
        """Get system-level metrics"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0,
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            logging.error(f"Failed to get system metrics: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'load_average': 0,
                'process_count': 0
            }
    
    def get_application_metrics(self):
        """Get application-level metrics"""
        response_times = self.metrics['response_times']
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            **self.metrics,
            'avg_response_time': avg_response_time,
            'p95_response_time': self.percentile(response_times, 95),
            'p99_response_time': self.percentile(response_times, 99)
        }
    
    @staticmethod
    def percentile(data, percentile):
        """Calculate percentile of a list"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100.0) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def setup_startup_time(self):
        """Record application startup time"""
        self.start_time = time.time()

# Performance monitoring decorator
def monitor_performance(metric_name):
    """Decorator to monitor function performance"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                logging.info(f"Performance: {metric_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logging.error(f"Performance: {metric_name} failed after {duration:.3f}s: {e}")
                raise
        return decorated_function
    return decorator

# Log configuration for structured logging
class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request context if available
        if hasattr(g, 'request_id'):
            log_entry['request_id'] = g.request_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_structured_logging():
    """Setup structured JSON logging for production"""
    if os.getenv('FLASK_ENV') == 'production':
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.handlers = [handler]
        
        # Reduce werkzeug noise in production
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        logging.info("Structured JSON logging initialized")

# Alert system (basic implementation)
class AlertManager:
    """Basic alert management system"""
    
    def __init__(self):
        self.alerts = []
        self.webhooks = {
            'slack': os.getenv('SLACK_WEBHOOK_URL'),
            'discord': os.getenv('DISCORD_WEBHOOK_URL')
        }
    
    def send_alert(self, level, title, message, details=None):
        """Send alert to configured channels"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'title': title,
            'message': message,
            'details': details or {}
        }
        
        self.alerts.append(alert)
        logging.error(f"Alert {level}: {title} - {message}")
        
        # Send to external services if configured
        if self.webhooks['slack'] and level in ['critical', 'error']:
            self._send_slack_alert(alert)
    
    def _send_slack_alert(self, alert):
        """Send alert to Slack webhook"""
        try:
            import requests
            
            color = {
                'critical': 'danger',
                'error': 'warning',
                'warning': 'warning',
                'info': 'good'
            }.get(alert['level'], 'warning')
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': f"🚨 {alert['title']}",
                    'text': alert['message'],
                    'fields': [
                        {'title': 'Level', 'value': alert['level'], 'short': True},
                        {'title': 'Time', 'value': alert['timestamp'], 'short': True}
                    ]
                }]
            }
            
            requests.post(self.webhooks['slack'], json=payload, timeout=5)
            logging.info(f"Alert sent to Slack: {alert['title']}")
            
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {e}")

# Global alert manager instance
alert_manager = AlertManager()
# Contract Explainer - Production Deployment Guide

## 🚀 Quick Start

The Contract Explainer is ready for production deployment with multiple cloud platform options. This guide covers everything from local development to production monitoring.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Options](#deployment-options)
4. [Security Configuration](#security-configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- Python 3.11+
- Git
- Domain name (recommended)
- Deepseek AI API key

### Platform-Specific
- **Heroku**: Heroku CLI
- **Railway**: Railway CLI
- **Render**: GitHub account
- **Docker**: Docker & Docker Compose

## Environment Setup

### 1. Clone and Setup

```bash
git clone <your-repo>
cd contract-explainer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
DEEPSEEK_API_KEY=your_deepseek_api_key_here
FLASK_SECRET_KEY=your_super_secret_key_here

# Optional but recommended
GOOGLE_ADSENSE_CLIENT_ID=ca-pub-your-publisher-id
SENTRY_DSN=your_sentry_dsn_here
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Production specific
FLASK_ENV=production
FLASK_DEBUG=0
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Deployment Options

### Option 1: Automated Universal Deployment

```bash
# Interactive deployment
python deploy/deploy.py

# Direct platform deployment
python deploy/deploy.py --platform railway
python deploy/deploy.py --platform heroku
python deploy/deploy.py --platform render
```

### Option 2: Platform-Specific Deployment

#### Heroku Deployment

```bash
# Install Heroku CLI and login
heroku login

# Run deployment script
python deploy/heroku.py

# Or manual deployment
heroku create your-app-name
git push heroku main
```

#### Railway Deployment

```bash
# Install Railway CLI and login
npm install -g @railway/cli
railway login

# Deploy
python deploy/railway.py

# Or manual
railway link
railway up
```

#### Render Deployment

```bash
# Deploy via GitHub integration
python deploy/render.py

# Then connect your GitHub repo at render.com
```

#### Docker Deployment

```bash
# Local development
docker-compose -f docker-compose.dev.yml up

# Production
cp .env.example .env  # Configure your variables
docker-compose up -d
```

### Option 3: CI/CD with GitHub Actions

1. Fork/clone the repository
2. Set up repository secrets:
   ```
   DEEPSEEK_API_KEY
   FLASK_SECRET_KEY
   HEROKU_API_KEY (if using Heroku)
   RAILWAY_TOKEN (if using Railway)
   SENTRY_DSN (optional)
   SLACK_WEBHOOK_URL (optional)
   ```

3. Push to main branch - automatic deployment triggers

## Security Configuration

### Essential Security Setup

1. **HTTPS**: Always use HTTPS in production
2. **Environment Variables**: Never commit secrets
3. **Rate Limiting**: Configured automatically (Redis recommended)
4. **CORS**: Configure `ALLOWED_ORIGINS` for your domain
5. **CSP**: Content Security Policy is auto-configured

### Security Headers Checklist

The application automatically sets:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)
- Content Security Policy
- Rate limiting headers

### File Upload Security

- Maximum 16MB file size
- Allowed extensions: PDF, DOCX, DOC, TXT
- Filename sanitization
- Content-Type validation
- Virus scanning (recommended for production)

## Monitoring & Logging

### Health Checks

- Basic: `GET /health`
- Detailed: `GET /health/detailed`
- Metrics: `GET /metrics`

### Logging Levels

```bash
# Development
export LOG_LEVEL=DEBUG

# Production
export LOG_LEVEL=INFO
```

### Sentry Error Tracking

1. Sign up at [sentry.io](https://sentry.io)
2. Create a new project
3. Add `SENTRY_DSN` to environment variables
4. Errors are automatically tracked

### Monitoring Endpoints

| Endpoint | Purpose | Response Format |
|----------|---------|-----------------|
| `/health` | Basic health check | JSON |
| `/health/detailed` | System metrics | JSON |
| `/metrics` | Prometheus metrics | Text |

### Performance Monitoring

The application tracks:
- Request/response times
- Error rates
- File upload metrics
- System resource usage
- Active user counts

### Alerting

Configure webhook URLs for automatic alerts:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

## Performance Optimization

### Recommended Production Settings

```bash
# Gunicorn workers (adjust based on CPU cores)
WEB_CONCURRENCY=4

# Redis for session storage and rate limiting
REDIS_URL=redis://localhost:6379

# CDN for static assets (optional)
CDN_DOMAIN=https://cdn.yourdomain.com
```

### Scaling Guidelines

| Users | Platform Recommendation | Configuration |
|-------|------------------------|---------------|
| 0-1K | Render/Railway Free | 1 instance |
| 1K-10K | Railway Pro | 2-3 instances |
| 10K-50K | Heroku Standard | Load balancer |
| 50K+ | Custom infrastructure | Kubernetes |

### Database Considerations

Current architecture is stateless, but for future features:
- User accounts: PostgreSQL
- Analytics: ClickHouse or BigQuery
- File storage: AWS S3 or similar

## Configuration Reference

### Complete Environment Variables

```bash
# Core Application
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=your-secret-key
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# AI Service
DEEPSEEK_API_KEY=your-api-key

# Security
ALLOWED_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_HOUR=100

# File Handling
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO

# External Services
GOOGLE_ADSENSE_CLIENT_ID=ca-pub-your-id
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX

# Alerting
SLACK_WEBHOOK_URL=your-slack-webhook
DISCORD_WEBHOOK_URL=your-discord-webhook

# Database (future)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis (caching/sessions)
REDIS_URL=redis://localhost:6379
REDIS_PRIVATE_URL=redis://localhost:6379  # Railway format

# Platform specific
PORT=5001  # Railway/Heroku
RENDER_GIT_COMMIT=commit-hash  # Render
```

### Nginx Configuration (VPS Deployment)

If deploying to a VPS, use the included `nginx.conf`:

```bash
# Copy and customize
cp nginx.conf /etc/nginx/sites-available/contract-explainer
ln -s /etc/nginx/sites-available/contract-explainer /etc/nginx/sites-enabled/

# Update with your domain
sed -i 's/your-domain.com/yourdomain.com/g' /etc/nginx/sites-enabled/contract-explainer

# Get SSL certificate
certbot --nginx -d yourdomain.com

# Restart nginx
systemctl restart nginx
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
ModuleNotFoundError: No module named 'security'
```

**Solution**: Ensure all files are in the same directory and dependencies are installed.

#### 2. Redis Connection Issues

```bash
redis.exceptions.ConnectionError: Connection refused
```

**Solution**: 
- Local: Start Redis server
- Production: Check `REDIS_URL` environment variable

#### 3. File Upload Failures

```bash
413 Request Entity Too Large
```

**Solution**: Check `MAX_CONTENT_LENGTH` and reverse proxy settings.

#### 4. API Key Issues

```bash
API Error: 401 - Unauthorized
```

**Solution**: Verify `DEEPSEEK_API_KEY` is correctly set and valid.

### Debug Mode

Enable debug logging:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
```

### Health Check Failures

If health checks fail:

1. Check application logs
2. Verify environment variables
3. Test database connections
4. Check system resources

### Performance Issues

Monitor these metrics:

```bash
# Check system resources
curl https://yourdomain.com/health/detailed

# Check application metrics
curl https://yourdomain.com/metrics

# Check error rates
grep "ERROR" app.log | wc -l
```

## Production Checklist

Before going live:

### Security
- [ ] HTTPS enabled
- [ ] Environment variables set
- [ ] Rate limiting configured  
- [ ] CORS origins specified
- [ ] Security headers verified
- [ ] File upload validation tested

### Performance
- [ ] Load testing completed
- [ ] Database connections optimized
- [ ] Caching configured
- [ ] CDN setup (if needed)
- [ ] Monitoring enabled

### Operations
- [ ] Health checks responding
- [ ] Error tracking configured
- [ ] Backup strategy defined
- [ ] Scaling plan documented
- [ ] Alert notifications tested

### Legal & Compliance
- [ ] Privacy policy added
- [ ] Terms of service updated
- [ ] GDPR compliance (if applicable)
- [ ] Data retention policy defined
- [ ] Legal disclaimers included

## Support

For deployment issues:

1. Check application logs
2. Review this documentation
3. Test with sample files
4. Monitor system resources
5. Review security configurations

### Emergency Procedures

#### Application Down

1. Check health endpoints
2. Review recent deployments
3. Check system resources
4. Restart application
5. Notify users if extended

#### High Error Rate

1. Check error logs
2. Monitor system metrics
3. Verify external dependencies
4. Consider temporary rate limiting
5. Rollback if necessary

#### Performance Degradation

1. Monitor response times
2. Check database performance
3. Review system resources
4. Scale horizontally if needed
5. Optimize bottlenecks

---

**Happy Deploying!** 🚀

Your Contract Explainer is now ready for production with enterprise-grade security, monitoring, and scalability.
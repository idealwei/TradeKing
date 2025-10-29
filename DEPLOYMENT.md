# TradeKing Deployment Guide

This guide covers deploying TradeKing in various environments.

## Prerequisites

- Python 3.9 or higher
- pip package manager
- API keys for:
  - OpenAI (for GPT-5) or DeepSeek
  - Longbridge trading platform

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/idealwei/TradeKing.git
cd TradeKing
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using the package:

```bash
pip install -e .
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure your API keys and settings:

```env
# Model Configuration
TRADE_AGENT_MODEL=gpt5  # or deepseek
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Longbridge Configuration
LONGBRIDGE_ACCESS_TOKEN=your_longbridge_token_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Scheduler (optional)
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=5
```

### 4. Initialize Database

The database will be automatically initialized on first run, but you can manually initialize it:

```python
from storage import init_db
init_db()
```

## Running the Application

### Development Mode

Run the FastAPI server with auto-reload:

```bash
python -m backend.app
```

Or using uvicorn directly:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- Web Dashboard: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### Production Mode

For production, use a production-grade ASGI server:

```bash
# Using uvicorn with workers
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn with uvicorn workers
gunicorn backend.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Running the Trading Agent Standalone

You can run the trading agent without the web interface:

```bash
python -m trade_agent.runtime
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t tradeking:latest .
```

### Run with Docker

```bash
docker run -d \
  --name tradeking \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e LONGBRIDGE_ACCESS_TOKEN=your_token \
  -v $(pwd)/data:/app/data \
  tradeking:latest
```

### Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  tradeking:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LONGBRIDGE_ACCESS_TOKEN=${LONGBRIDGE_ACCESS_TOKEN}
      - TRADE_AGENT_MODEL=gpt5
      - SCHEDULER_ENABLED=true
      - DATABASE_URL=sqlite:///./data/tradeking.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

Run with:

```bash
docker-compose up -d
```

## Cloud Deployment

### AWS EC2

1. Launch an EC2 instance (t3.small or larger recommended)
2. Install Python 3.9+ and dependencies
3. Clone the repository
4. Configure environment variables
5. Run with systemd service:

```ini
# /etc/systemd/system/tradeking.service
[Unit]
Description=TradeKing Trading Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/TradeKing
Environment="PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/ubuntu/TradeKing/.env
ExecStart=/usr/bin/python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable tradeking
sudo systemctl start tradeking
```

### Heroku

1. Create a `Procfile`:

```
web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```

2. Deploy:

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
heroku config:set LONGBRIDGE_ACCESS_TOKEN=your_token
git push heroku main
```

### Railway / Render

These platforms support automatic deployment from Git:

1. Connect your GitHub repository
2. Configure environment variables in the dashboard
3. Set start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

## Database Migration

If you make changes to database models, use Alembic for migrations:

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

## Monitoring & Logging

### Logs

Logs are written to:
- Console (stdout/stderr)
- `logs/tradeking.log` (if LOG_FILE is set)

View logs:

```bash
# Docker
docker logs -f tradeking

# Systemd
sudo journalctl -u tradeking -f

# File
tail -f logs/tradeking.log
```

### Health Checks

Monitor the health endpoint:

```bash
curl http://localhost:8000/api/health
```

### Metrics (Optional)

For production monitoring, integrate with:
- Prometheus + Grafana
- Datadog
- New Relic
- CloudWatch (AWS)

## Security Considerations

1. **API Keys**: Never commit `.env` files. Use secret managers in production.
2. **HTTPS**: Use a reverse proxy (Nginx, Caddy) with SSL certificates.
3. **Firewall**: Restrict access to necessary ports only.
4. **Authentication**: Implement authentication for multi-user deployments.
5. **Rate Limiting**: Add rate limiting to prevent abuse.

## Backup Strategy

### Database Backup

```bash
# Backup SQLite database
cp tradeking.db tradeking.db.backup.$(date +%Y%m%d)

# Or use sqlite3 dump
sqlite3 tradeking.db .dump > backup.sql
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /home/ubuntu/TradeKing/scripts/backup.sh
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and Python path is correct.
2. **Database Errors**: Check file permissions and disk space.
3. **API Errors**: Verify API keys and network connectivity.
4. **Port Already in Use**: Change SERVER_PORT or kill existing process.

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
DEBUG=true
```

### Testing API

Use the interactive API docs at http://localhost:8000/docs to test endpoints.

## Scaling

For high-traffic deployments:

1. **Use PostgreSQL** instead of SQLite:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/tradeking
   ```

2. **Add Redis** for caching:
   ```python
   # Implement caching layer for market data
   ```

3. **Load Balancer**: Use multiple instances behind a load balancer.

4. **Separate Workers**: Run scheduler in a separate process.

## Support

For issues and questions:
- GitHub Issues: https://github.com/idealwei/TradeKing/issues
- Documentation: See README.md

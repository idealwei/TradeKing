# Changelog

All notable changes to TradeKing will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-29

### Added

#### Core Agent (Milestone 1)
- LangGraph-based trading agent with multi-node workflow
- Support for GPT-5 and DeepSeek models via OpenAI-compatible API
- Longbridge API integration for:
  - Account overview
  - Position tracking
  - Order history
  - Market data snapshots
  - Asset information
- Configurable prompt templates for trading decisions
- CLI runtime for standalone execution

#### Backend Service (Milestone 2)
- FastAPI-based REST API server
- Endpoints for:
  - `/api/health` - Health check and system status
  - `/api/decisions/*` - Trading decision management
  - `/api/models/*` - Model performance metrics
  - `/api/portfolio/*` - Portfolio tracking and equity curves
- SQLAlchemy ORM with SQLite database
- Database models for:
  - Trading decisions with full context
  - Model performance tracking
  - Portfolio snapshots
- Repository pattern for data access
- Background scheduler for automated trading (APScheduler)
- CORS support for frontend integration

#### Web Dashboard (Milestone 2)
- Modern dark-themed UI inspired by RockAlpha
- Dashboard page with:
  - Real-time statistics (decisions, portfolio value, P&L)
  - Model performance comparison cards
  - Latest trading decision display
  - Equity curve chart with linear/log scale toggle
- Portfolio page with:
  - Portfolio overview statistics
  - Holdings table with P&L tracking
  - Asset allocation doughnut chart
- Decisions log page with:
  - Paginated decision history
  - Model filtering
  - Decision detail modal with full context
- Responsive design for mobile and desktop
- Auto-refresh every 30 seconds
- Chart.js integration for data visualization

#### Configuration & Deployment
- Environment-based configuration (.env)
- Docker support with Dockerfile and docker-compose.yml
- Comprehensive deployment guide
- Project structure following best practices
- Dependencies management (requirements.txt, pyproject.toml)

### Infrastructure
- Git repository initialization
- README with PRD documentation
- License and contribution guidelines
- Example environment configuration

## [Unreleased]

### Planned (Milestone 3 - Automation & Compliance)
- Position sizing limits and risk guardrails
- Stop-loss enforcement checks
- Prometheus metrics export
- Grafana dashboards
- Extensive audit logging
- Email/Slack alerting
- Multi-user authentication
- PostgreSQL support for production
- Redis caching layer
- Historical backtesting module

[0.1.0]: https://github.com/idealwei/TradeKing/releases/tag/v0.1.0

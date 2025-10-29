# TradeKing - AI Trading Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

> **TradeKing** is an autonomous U.S. equities trading agent tailored for retail quants who want AI-driven trading decisions without building the infrastructure from scratch.

The agent analyzes account data, market snapshots, open positions, and order history, then produces actionable trade recommendations. It is powered by **LangGraph** for agent orchestration, leverages OpenAI-compatible LLMs (**GPT-5** or **DeepSeek**) for strategy synthesis, and connects to the **Longbridge API** for live brokerage data.

## ✨ Features

- 🤖 **Multi-Model Support**: Seamlessly switch between GPT-5 and DeepSeek
- 📊 **Real-time Dashboard**: Modern web UI with live trading signals and portfolio tracking
- 📈 **Equity Curve Visualization**: Track performance with interactive charts
- 🔄 **Automated Execution**: Scheduled trading decisions every 5 minutes (configurable)
- 💾 **Historical Tracking**: SQLite database storing all decisions and performance metrics
- 🔌 **REST API**: Full-featured FastAPI backend for integration
- 🐳 **Docker Support**: One-command deployment with Docker Compose

## 🎯 Product Overview

## 2. Goals & Success Criteria
- **Deliver trustworthy trade recommendations**: Provide clear buy/sell/hold actions with risk controls (take-profit and stop-loss) aligned to the competition rules.
- **Support multiple foundation models**: Allow seamless switching between GPT-5 and DeepSeek via environment configuration.
- **Integrate with Longbridge brokerage data**: Pull account balances, positions, orders, and market snapshots to ground model outputs in real data.
- **Expose insights through a UI**: Visualize buy/sell signals, trade history, and portfolio equity curve to build user confidence.

**Success Metrics**
- Decision latency under 10 seconds per run (LLM call + data fetch).
- ≥90% of generated decisions include both take-profit and stop-loss targets.
- UI latency <1 second for dashboard refresh using cached agent output.
- Daily active users accessing the dashboard ≥ 5 within the first month (internal pilot).

## 3. Target Users & Personas
- **Retail Quant Trader**: Wants to experiment with AI-driven strategies without managing infra. Needs transparent guidance and risk controls.
- **AI Trading Enthusiast**: Interested in comparing different LLM strategies; values quick model switching.
- **Operations Analyst**: Monitors compliance with trading rules; needs logs of orders and rationale.

## 4. User Scenarios
1. **Daily Trading Session**: Trader runs the agent every market interval. The dashboard highlights recommended trades, shows rationale, and charts portfolio P&L.
2. **Model Benchmarking**: User toggles between GPT-5 and DeepSeek, compares historical recommendations and performance metrics week-over-week.
3. **Risk Review**: Analyst filters the decision log to ensure every trade has valid stop-loss/take-profit levels before approving automated execution.

## 5. Key Features & Requirements
### 5.1 Trading Agent
- LangGraph-based pipeline with nodes for data ingestion, prompt composition, and LLM invocation.
- Parameterizable via environment variables (`TRADE_AGENT_MODEL`, `TRADE_AGENT_TEMPERATURE`, etc.).
- Longbridge API integration covering account overview, positions, order history, assets, and market snapshot.
- Prompt template (`prompts/trade_prompts.py`) enforcing output format: `SIDE | SYMBOL | LEVERAGE | SIZE | ENTRY | EXIT PLAN | UNREALIZED P&L`.

### 5.2 Model Routing
- Support GPT-5 (`OPENAI_API_KEY`) and DeepSeek (`DEEPSEEK_API_KEY`) through the OpenAI SDK with custom base URLs.
- Hot swapping of models without code changes—driven by `.env` or runtime configuration.

### 5.3 Data Visualization UI (✅ Complete)
- **Dashboard**: Review latest recommendation, rationale, and risk levels with real-time stats.
- **Portfolio Tracker**: Display total capital curve, realized/unrealized P&L, asset allocation.
- **Decision Log**: Paginated table with timestamp, model used, symbols, and execution status.
- **Equity Curve**: Interactive Chart.js visualization with linear/log scale toggle.
- Tech Stack: Vanilla JavaScript + FastAPI for optimal performance and simplicity.

### 5.4 Observability & Logging
- Structured logs capturing request IDs, model choice, prompt metadata, and Longbridge API latency.
- Optional export to external monitoring (e.g., Prometheus/Grafana) for production readiness.

## 6. Architecture
```
Longbridge API ──▶ TradingDataFetcher ┐
                                      │
LangGraph StateGraph ──▶ Prompt Composer ──▶ Model Dispatcher (OpenAI SDK) ──▶ LLM (GPT-5 / DeepSeek)
                                      │
                                  Decision Output ──▶ UI / CLI Runner
```

**Modules**
- `trade_agent/config.py`: Configuration dataclasses and environment helpers.
- `trade_agent/models.py`: ModelDispatcher encapsulating OpenAI-compatible clients.
- `trade_agent/tools/longbridge.py`: API client and data formatter for prompt injection.
- `trade_agent/agent.py`: LangGraph workflow producing trading decisions.
- `trade_agent/runtime.py`: Entry point for CLI execution (`python -m trade_agent.runtime`).

## 7. Roadmap

### Milestone 1 – Core Agent (✅ Complete)
- ✅ Implement LangGraph workflow with Longbridge data sources
- ✅ Support GPT-5 and DeepSeek selection
- ✅ Provide CLI runner for manual execution

### Milestone 2 – UI & Distribution (✅ Complete)
- ✅ Build FastAPI backend service with REST endpoints
- ✅ Develop web dashboard for signals, equity curve, and model comparison
- ✅ Implement SQLite storage for historical decisions
- ✅ Background scheduler for automated execution
- 🔄 Authentication & multi-user support (planned)

### Milestone 3 – Automation & Compliance (Planned)
- Scheduler for automated intraday execution (e.g., using APScheduler or cloud cron).
- Risk guardrails: position sizing limits, stop-loss enforcement checks.
- Extensive logging, monitoring, and alerting.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- API keys for OpenAI (GPT-5) or DeepSeek
- Longbridge trading account and access token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/idealwei/TradeKing.git
   cd TradeKing
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   # Start the web server
   python -m backend.app

   # Or use the CLI
   python -m trade_agent.runtime
   ```

5. **Access the dashboard**
   Open http://localhost:8000 in your browser

### Docker Deployment

```bash
docker-compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📖 Usage

### Running a Single Decision

```python
from trade_agent.runtime import run_once

# Execute a trading decision
decision = run_once(symbols=["NVDA.US", "TSLA.US"])
print(decision)
```

### Using the REST API

```bash
# Health check
curl http://localhost:8000/api/health

# Execute a decision
curl -X POST http://localhost:8000/api/decisions/execute \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["NVDA.US", "TSLA.US"]}'

# Get latest decisions
curl http://localhost:8000/api/decisions/latest?limit=10

# Get model performance
curl http://localhost:8000/api/models/performance
```

### Configuration

All configuration is done via environment variables in `.env`:

```env
# Model Selection
TRADE_AGENT_MODEL=gpt5  # or deepseek
TRADE_AGENT_TEMPERATURE=0.4
TRADE_AGENT_MAX_OUTPUT_TOKENS=1024

# API Keys
OPENAI_API_KEY=your_openai_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
LONGBRIDGE_ACCESS_TOKEN=your_longbridge_token

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Scheduler (automated trading)
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=5
```

## 📁 Project Structure

```
TradeKing/
├── trade_agent/          # Core trading agent
│   ├── agent.py         # LangGraph workflow
│   ├── config.py        # Configuration management
│   ├── models.py        # Model dispatcher
│   ├── runtime.py       # CLI runner
│   └── tools/
│       └── longbridge.py # Longbridge API client
├── backend/             # FastAPI backend
│   ├── app.py          # Application factory
│   ├── schemas.py      # Pydantic models
│   ├── scheduler.py    # Background scheduler
│   └── routers/        # API endpoints
├── storage/             # Data persistence
│   ├── database.py     # SQLAlchemy setup
│   ├── models.py       # Database models
│   └── repository.py   # Data access layer
├── frontend/            # Web dashboard
│   ├── index.html      # Main dashboard
│   ├── portfolio.html  # Portfolio page
│   ├── decisions.html  # Decision log
│   └── assets/         # CSS/JS/images
├── prompts/             # Trading prompts
│   └── trade_prompts.py
└── docs/                # Documentation
```

## 9. Risks & Mitigations
- **Model drift / hallucinations**: Regularly review outputs, incorporate guardrails or scoring.
- **API rate limits**: Cache Longbridge responses per interval; monitor usage.
- **UI adoption**: Gather feedback from pilot traders to adjust dashboard KPIs.
- **Security**: Store API keys securely (env vars, secret managers); enforce SSH-only Git pushes.

## 10. Release Plan
1. Finalize core agent validation with paper trading logs.
2. Implement backend service and dashboard MVP.
3. Conduct internal beta with limited accounts.
4. Iterate on performance metrics, add automation features.
5. Public beta with documentation and onboarding checklist.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [RockAlpha](https://rockalpha.rockflow.ai/) interface design
- Reference implementation from [AI-Trader](https://github.com/HKUDS/AI-Trader)
- Built with [LangGraph](https://github.com/langchain-ai/langgraph) and [FastAPI](https://fastapi.tiangolo.com/)

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading stocks carries risk. Past performance does not guarantee future results. Always conduct your own research and consult with a financial advisor before making investment decisions.

## 📧 Contact

**idealwei** - [@idealwei](https://github.com/idealwei)

Project Link: [https://github.com/idealwei/TradeKing](https://github.com/idealwei/TradeKing)

---

Made with ❤️ for the algorithmic trading community

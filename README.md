# TradeKing Trading Agent PRD

## 1. Product Overview
TradeKing is an autonomous U.S. equities trading agent tailored for retail quants who want AI-driven trading decisions without building the infrastructure from scratch. The agent analyzes account data, market snapshots, open positions, and order history, then produces actionable trade recommendations every five minutes. It is powered by LangGraph for agent orchestration, leverages OpenAI-compatible LLMs (GPT-5 or DeepSeek) for strategy synthesis, and connects to the Longbridge API for live brokerage data.

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

### 5.3 Data Visualization UI (Planned)
- **Dashboard**: Review latest recommendation, rationale, and risk levels.
- **Signal Timeline**: Chart buy/sell points against price series for tracked symbols.
- **Portfolio Tracker**: Display total capital curve, realized/unrealized P&L, and commission impact.
- **Decision Log**: Paginated table with timestamp, model used, symbols, and execution status.
- Web technology stack TBD (React + FastAPI suggested) with shared data contracts from the agent runtime.

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
### Milestone 1 – Core Agent (Complete)
- Implement LangGraph workflow with Longbridge data sources.
- Support GPT-5 and DeepSeek selection.
- Provide CLI runner for manual execution.

### Milestone 2 – UI & Distribution (Planned)
- Build backend service (FastAPI or Flask) to expose REST endpoints for latest decision and historical logs.
- Develop web dashboard for signals, equity curve, and model comparison.
- Implement caching/storage for historical decisions (SQLite/PostgreSQL).
- Add authentication & multi-user support.

### Milestone 3 – Automation & Compliance (Planned)
- Scheduler for automated intraday execution (e.g., using APScheduler or cloud cron).
- Risk guardrails: position sizing limits, stop-loss enforcement checks.
- Extensive logging, monitoring, and alerting.

## 8. Dependencies & Setup
```
pip install langgraph openai requests
export OPENAI_API_KEY=...
export DEEPSEEK_API_KEY=...
export LONGBRIDGE_ACCESS_TOKEN=...
python -m trade_agent.runtime
```
Optional environment variables:
- `TRADE_AGENT_MODEL` (`gpt5` or `deepseek`)
- `TRADE_AGENT_TEMPERATURE`
- `TRADE_AGENT_MAX_OUTPUT_TOKENS`
- `OPENAI_BASE_URL`, `DEEPSEEK_BASE_URL`
- `LONGBRIDGE_BASE_URL`, `LONGBRIDGE_TIMEOUT`

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

## 11. Open Questions
- Which charting library is preferred for the dashboard (e.g., ECharts, Plotly)?
- What compliance requirements exist for automated Longbridge trading?
- Should strategy outputs be persisted for backtesting? If so, select storage engine.

---
Maintained by [idealwei](https://github.com/idealwei). Contributions via issues and PRs are welcome once the roadmap milestones are in progress.

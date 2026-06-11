# QuanTrade AI Agent

Smarter signals. Calmer trading.

QuanTrade AI Agent is a crypto behavioral-intelligence and paper-trading platform. The MVP is deliberately conservative: it detects evidence, calculates deterministic scores, applies risk blocks, and uses AI only to explain structured data. It does not execute live trades.

## Current Status

Milestone 0 and the Milestone 1 foundation are scaffolded:

- Production-shaped monorepo
- FastAPI backend source
- React/Vite frontend source
- Deterministic fixture replay data
- Decimal-safe local order-book synchronization
- Data-health API for fixture replay
- Deterministic paper-order, portfolio, journal, and performance API behavior
- Persistence-ready repository layer with in-memory fixture implementation
- SQL schema, SQLAlchemy models, and Alembic configuration
- SQLAlchemy repository implementation for database-backed persistence
- Streamlit test harness for trying the app while the production UI is still being built
- Streamlit Cloud dependency files and pydantic-free schema path for deployment
- Onboarding risk-profile defaults and validation
- Core feature, signal, risk, paper-trading, and AI-explanation modules
- Standard-library unit tests for critical deterministic logic
- Docker Compose, Makefile, CI, and documentation skeleton

The local Codex runtime does not currently include FastAPI, SQLAlchemy, Vite, or React packages, so install dependencies with network access before running the full stack.

## Safety Limits

- Paper trading only
- No live order submission code
- No leverage or margin workflows
- No hidden exchange trading endpoints
- Fixture data is labeled as demo data
- AI explanations cannot override risk controls or invent market values

## Quick Start

```bash
make setup
make test-unit
make migrate
make dev
```

Backend API: `http://localhost:8000`

Frontend: `http://localhost:5173`

## Temporary Streamlit Test Harness

Use this while the full React/FastAPI stack is still being wired:

```bash
make streamlit
```

Streamlit app: `http://localhost:8502`

This harness uses deterministic fixture mode and the same service payload builders as the API. It includes onboarding risk-profile defaults, scanner, signal detail, replay health, and paper portfolio views. It is demo/paper mode only.

## Environment

Copy `.env.example` to `.env.local` and set values as needed.

`QUANTRADE_MODE` supports:

- `fixture`
- `live`
- `test`

The app works without `OPENAI_API_KEY`. When the key is present, the AI explanation provider may use OpenAI after schema validation and guardrails.

## Important Commands

```bash
make setup
make dev
make stop
make seed
make fixture-replay
make streamlit
make lint
make typecheck
make test
make test-unit
make test-integration
make test-e2e
make migrate
make migration
make build
```

## Documentation

- [Implementation Plan](docs/implementation-plan.md)
- [Architecture](docs/architecture.md)
- [Strategy Specification](docs/strategy-specification.md)
- [Paper Trading Model](docs/paper-trading-model.md)
- [Security](docs/security.md)
- [Runbook](docs/runbook.md)

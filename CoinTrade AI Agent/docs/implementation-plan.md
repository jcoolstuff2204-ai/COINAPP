# Implementation Plan

## Current-State Assessment

The repository started empty except for `.env.local`. There were no existing source files, tests, build scripts, or architecture conventions to preserve.

The local Codex runtime has Python, NumPy, Pandas, and Pydantic available, but does not currently have FastAPI, SQLAlchemy, pytest, React, Vite, or TypeScript installed. The project therefore includes dependency manifests and standard-library tests that can run immediately, while full-stack commands require `make setup`.

## Architecture Proposal

QuanTrade is organized as a monorepo:

- `apps/api`: FastAPI app and API composition
- `apps/web`: React/Vite frontend
- `services`: deterministic domain engines
- `services/persistence`: repository contracts and testable in-memory persistence
- `packages/schemas`: shared typed domain models
- `packages/test_fixtures`: deterministic fixture events
- `docs`: product and engineering documentation
- `infrastructure`: Docker and migration assets
- `tests`: deterministic unit and integration tests

Deterministic services own calculations. The AI service may only transform validated signal evidence into structured explanation text.

## Risks And Unknowns

- Full dependency installation needs network access.
- Live exchange integration is intentionally not implemented yet.
- Database migrations have SQL, SQLAlchemy models, and Alembic configuration, but database-backed repository methods still need implementation after dependency installation.
- TimescaleDB support depends on the target database environment.
- Legal and compliance disclaimers may need review before real user deployment.

## Milestone Checklist

- [x] Milestone 0: repository assessment, plan, commands, docs
- [x] Milestone 1 foundation scaffold: monorepo, API/web source, Docker, env validation, health route, CI skeleton
- [x] Milestone 2 partial: deterministic fixture data, feature/risk/signal/paper engines, replay script, local order-book synchronization, data-health API, deterministic paper-order lifecycle
- [x] Persistence scaffold: SQL schema, SQLAlchemy model definitions, Alembic config, repository contract, in-memory repository
- [x] Database repository implementation: SQLAlchemy repository and tested serializer mappings
- [x] Temporary Streamlit test harness for fixture scanner, signal detail, replay health, and paper portfolio
- [ ] Milestone 2 complete: run migrations against Postgres, verify database repository integration, replay controls connected to a running UI, order-book service backed by durable storage
- [ ] Milestone 3: live public market data provider
- [ ] Milestone 4: full feature engine
- [ ] Milestone 5: scanner and Momentum Ignition production workflow
- [ ] Milestone 6: manipulation and market regime engines
- [ ] Milestone 7: paper trading persistence and lifecycle
- [ ] Milestone 8: journal and performance analytics
- [ ] Milestone 9: optional OpenAI analyst
- [ ] Milestone 10: production hardening

## Commands

```bash
make setup
make dev
make stop
make reset
make seed
make fixture-replay
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

## Architecture Decisions

1. The MVP defaults to `fixture` mode and labels fixture-derived UI as demo data.
2. Critical engines use `Decimal` for monetary and size calculations.
3. The first unit tests use `unittest` so they can run before dependency installation.
4. AI explanation has a deterministic template provider and a guarded provider interface for OpenAI.
5. Live exchange providers are represented by interfaces but omitted from this initial scaffold to avoid accidental trading scope.
6. Fixture replay now applies snapshot and update events through a local order-book engine, so invalid books and checksum failures can suspend calculations.
7. The initial database schema is committed as SQL and mirrored by SQLAlchemy model definitions for Alembic.
8. Paper order, portfolio, journal, and performance endpoints use a persistence-ready service layer with an in-memory repository by default.
9. A SQLAlchemy repository implementation exists, but live database verification is blocked until dependencies are installed.

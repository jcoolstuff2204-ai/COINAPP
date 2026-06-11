PYTHON ?= python3
NPM ?= npm
STREAMLIT_PORT ?= 8502
QUANTRADE_PYTHONPATH := apps/api:apps/streamlit:packages/schemas:services/user_profile:services/persistence:services/market_ingestion:services/feature_engine:services/risk_engine:services/signal_engine:services/paper_execution:services/ai_explanation

.PHONY: setup dev stop reset seed fixture-replay streamlit lint typecheck test test-unit test-integration test-e2e migrate migration build

setup:
	$(PYTHON) -m pip install -e "apps/api[dev]"
	cd apps/web && $(NPM) install

dev:
	docker compose up --build

stop:
	docker compose down

reset:
	docker compose down -v

seed:
	PYTHONPATH=$(QUANTRADE_PYTHONPATH) $(PYTHON) scripts/fixture_replay.py --summary

fixture-replay:
	PYTHONPATH=$(QUANTRADE_PYTHONPATH) $(PYTHON) scripts/fixture_replay.py

streamlit:
	PYTHONPATH=.streamlit_deps:$(QUANTRADE_PYTHONPATH):apps/streamlit $(PYTHON) -m streamlit run apps/streamlit/app.py --global.developmentMode=false --server.address localhost --server.port $(STREAMLIT_PORT)

lint:
	ruff check apps services packages tests
	cd apps/web && $(NPM) run lint

typecheck:
	mypy apps services packages
	cd apps/web && $(NPM) run typecheck

test: test-unit test-integration

test-unit:
	PYTHONPATH=$(QUANTRADE_PYTHONPATH) $(PYTHON) -m unittest discover -s tests -p "test_*.py"

test-integration:
	PYTHONPATH=$(QUANTRADE_PYTHONPATH) $(PYTHON) -m unittest discover -s tests -p "integration_*.py"

test-e2e:
	cd apps/web && $(NPM) run test:e2e

migrate:
	PYTHONPATH=$(QUANTRADE_PYTHONPATH) alembic -c infrastructure/migrations/alembic.ini upgrade head

migration:
	PYTHONPATH=$(QUANTRADE_PYTHONPATH) alembic -c infrastructure/migrations/alembic.ini revision --autogenerate -m "$${name:-migration}"

build:
	cd apps/web && $(NPM) run build

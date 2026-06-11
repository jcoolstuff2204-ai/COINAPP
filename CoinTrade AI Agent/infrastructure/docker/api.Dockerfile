FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app/apps/api:/app/packages/schemas:/app/services/persistence:/app/services/market_ingestion:/app/services/feature_engine:/app/services/risk_engine:/app/services/signal_engine:/app/services/paper_execution:/app/services/ai_explanation
COPY apps/api/pyproject.toml /app/apps/api/pyproject.toml
COPY packages /app/packages
COPY services /app/services
COPY apps/api /app/apps/api
RUN pip install --no-cache-dir -e /app/apps/api
EXPOSE 8000
CMD ["uvicorn", "quantrade_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

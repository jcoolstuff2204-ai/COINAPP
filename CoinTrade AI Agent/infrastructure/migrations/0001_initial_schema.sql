-- QuanTrade AI Agent initial MVP schema.
-- PostgreSQL-compatible SQL. Timescale hypertables can be added when the
-- deployment database has TimescaleDB installed.

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  display_name TEXT NOT NULL,
  development_auth_enabled BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS user_settings (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  virtual_starting_balance NUMERIC(20, 8) NOT NULL,
  risk_per_trade NUMERIC(8, 6) NOT NULL,
  daily_loss_limit NUMERIC(20, 8) NOT NULL,
  maximum_open_positions INTEGER NOT NULL,
  preferred_holding_minutes INTEGER NOT NULL,
  paper_trading_acknowledged BOOLEAN NOT NULL DEFAULT false,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS exchanges (
  id UUID PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  public_market_data_enabled BOOLEAN NOT NULL DEFAULT true,
  live_trading_enabled BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS assets (
  id UUID PRIMARY KEY,
  symbol TEXT NOT NULL,
  base_currency TEXT NOT NULL,
  quote_currency TEXT NOT NULL,
  display_name TEXT NOT NULL,
  exchange TEXT NOT NULL,
  product_id TEXT NOT NULL,
  status TEXT NOT NULL,
  listing_date DATE,
  eligibility_status TEXT NOT NULL,
  exclusion_reason TEXT,
  UNIQUE(exchange, symbol)
);

CREATE TABLE IF NOT EXISTS asset_eligibility_history (
  id UUID PRIMARY KEY,
  asset_id UUID NOT NULL REFERENCES assets(id),
  checked_at TIMESTAMPTZ NOT NULL,
  eligibility_status TEXT NOT NULL,
  exclusion_reason TEXT,
  metrics JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS trades (
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  trade_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  price NUMERIC(28, 12) NOT NULL,
  quantity NUMERIC(28, 12) NOT NULL,
  maker_side TEXT NOT NULL,
  aggressor_side TEXT NOT NULL,
  notional NUMERIC(28, 12) NOT NULL,
  PRIMARY KEY(exchange, symbol, trade_id)
);

CREATE TABLE IF NOT EXISTS candles (
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL,
  start_time TIMESTAMPTZ NOT NULL,
  open NUMERIC(28, 12) NOT NULL,
  high NUMERIC(28, 12) NOT NULL,
  low NUMERIC(28, 12) NOT NULL,
  close NUMERIC(28, 12) NOT NULL,
  volume NUMERIC(28, 12) NOT NULL,
  trade_count INTEGER NOT NULL,
  buy_volume NUMERIC(28, 12) NOT NULL,
  sell_volume NUMERIC(28, 12) NOT NULL,
  PRIMARY KEY(exchange, symbol, timeframe, start_time)
);

CREATE TABLE IF NOT EXISTS order_book_snapshots (
  id UUID PRIMARY KEY,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  checksum_status TEXT NOT NULL,
  valid BOOLEAN NOT NULL,
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS data_quality_events (
  id UUID PRIMARY KEY,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  event_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS feature_definitions (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  required_inputs JSONB NOT NULL,
  lookback_period TEXT NOT NULL,
  null_policy TEXT NOT NULL,
  UNIQUE(name, version)
);

CREATE TABLE IF NOT EXISTS feature_snapshots (
  id UUID PRIMARY KEY,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  feature_version TEXT NOT NULL,
  values JSONB NOT NULL,
  data_quality JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS market_regimes (
  id UUID PRIMARY KEY,
  regime TEXT NOT NULL,
  confidence NUMERIC(8, 4) NOT NULL,
  supporting_metrics JSONB NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL,
  rule_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS strategy_definitions (
  id UUID PRIMARY KEY,
  strategy_key TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS strategy_versions (
  id UUID PRIMARY KEY,
  strategy_id UUID NOT NULL REFERENCES strategy_definitions(id),
  version TEXT NOT NULL,
  status TEXT NOT NULL,
  parameters JSONB NOT NULL,
  weights JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  notes TEXT,
  UNIQUE(strategy_id, version)
);

CREATE TABLE IF NOT EXISTS signals (
  id UUID PRIMARY KEY,
  signal_id TEXT NOT NULL UNIQUE,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  strategy TEXT NOT NULL,
  strategy_version TEXT NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  behavioral_state TEXT NOT NULL,
  direction TEXT NOT NULL,
  opportunity_score NUMERIC(8, 4) NOT NULL,
  risk_score NUMERIC(8, 4) NOT NULL,
  manipulation_score NUMERIC(8, 4) NOT NULL,
  confidence NUMERIC(8, 4) NOT NULL,
  status TEXT NOT NULL,
  block_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
  plan JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_components (
  id UUID PRIMARY KEY,
  signal_id TEXT NOT NULL REFERENCES signals(signal_id),
  name TEXT NOT NULL,
  raw_value NUMERIC(28, 12) NOT NULL,
  normalized_score NUMERIC(8, 4) NOT NULL,
  weight NUMERIC(8, 6) NOT NULL,
  contribution NUMERIC(8, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_events (
  id UUID PRIMARY KEY,
  signal_id TEXT NOT NULL REFERENCES signals(signal_id),
  event_type TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS watchlist_items (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  signal_id TEXT NOT NULL REFERENCES signals(signal_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(user_id, signal_id)
);

CREATE TABLE IF NOT EXISTS paper_orders (
  id UUID PRIMARY KEY,
  order_id TEXT NOT NULL UNIQUE,
  signal_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL,
  order_type TEXT NOT NULL,
  requested_quantity NUMERIC(28, 12) NOT NULL,
  requested_price NUMERIC(28, 12) NOT NULL,
  submitted_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL,
  time_in_force TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_fills (
  id UUID PRIMARY KEY,
  fill_id TEXT NOT NULL UNIQUE,
  order_id TEXT NOT NULL REFERENCES paper_orders(order_id),
  timestamp TIMESTAMPTZ NOT NULL,
  price NUMERIC(28, 12) NOT NULL,
  quantity NUMERIC(28, 12) NOT NULL,
  fee NUMERIC(28, 12) NOT NULL,
  slippage NUMERIC(28, 12) NOT NULL,
  liquidity_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS paper_positions (
  id UUID PRIMARY KEY,
  position_id TEXT NOT NULL UNIQUE,
  symbol TEXT NOT NULL,
  strategy TEXT NOT NULL,
  side TEXT NOT NULL,
  quantity NUMERIC(28, 12) NOT NULL,
  average_entry NUMERIC(28, 12) NOT NULL,
  stop_price NUMERIC(28, 12) NOT NULL,
  targets JSONB NOT NULL,
  realized_pnl NUMERIC(28, 12) NOT NULL DEFAULT 0,
  unrealized_pnl NUMERIC(28, 12) NOT NULL DEFAULT 0,
  fees NUMERIC(28, 12) NOT NULL DEFAULT 0,
  opened_at TIMESTAMPTZ NOT NULL,
  closed_at TIMESTAMPTZ,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  timestamp TIMESTAMPTZ NOT NULL,
  equity NUMERIC(28, 12) NOT NULL,
  cash NUMERIC(28, 12) NOT NULL,
  realized_pnl NUMERIC(28, 12) NOT NULL,
  unrealized_pnl NUMERIC(28, 12) NOT NULL,
  open_risk NUMERIC(28, 12) NOT NULL
);

CREATE TABLE IF NOT EXISTS journal_entries (
  id UUID PRIMARY KEY,
  signal_id TEXT NOT NULL,
  position_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  pnl NUMERIC(28, 12) NOT NULL,
  r_multiple NUMERIC(12, 6) NOT NULL,
  rule_compliance JSONB NOT NULL,
  user_note TEXT,
  emotion_tag TEXT,
  ai_review JSONB
);

CREATE TABLE IF NOT EXISTS discipline_events (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  signal_id TEXT,
  position_id TEXT,
  event_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  message TEXT NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  alert_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  read_at TIMESTAMPTZ,
  dedupe_key TEXT
);

CREATE TABLE IF NOT EXISTS ai_explanations (
  id UUID PRIMARY KEY,
  signal_id TEXT NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL,
  model TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY,
  actor_id UUID,
  action TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS system_health_events (
  id UUID PRIMARY KEY,
  component TEXT NOT NULL,
  status TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_trades_symbol_time ON trades(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_candles_symbol_timeframe_time ON candles(symbol, timeframe, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_feature_snapshots_symbol_time ON feature_snapshots(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_signals_status_score ON signals(status, opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_signal_events_signal_time ON signal_events(signal_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_user_created ON alerts(user_id, created_at DESC);


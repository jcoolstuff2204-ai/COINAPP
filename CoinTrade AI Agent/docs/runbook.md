# Runbook

## Feed Disconnected

Show feed disconnected, suspend signals, log the provider and symbol, and retry with exponential backoff.

## Checksum Mismatch

Mark the order book invalid, suspend calculations for that symbol, request a new snapshot, and write a data-quality event.

Current fixture behavior: `checksum_failure_events.json` marks the local book invalid and returns `checksum_status=failed`.

## Database Failure

Report degraded system status, stop persistence-dependent workflows, and keep API errors structured with request IDs.

Before enabling database-backed mode, run `make migrate` and verify the SQLAlchemy repository can save and read a fixture signal, data-health event, paper order, position, and journal entry.

## Redis Failure

Disable transient pub/sub features and continue read-only API operations when possible.

## High Processing Lag

Show scanner lag, suspend stale signals, and record processing-lag metrics.

## Bad Deployment Rollback

Stop the stack, restore the last known-good image and migration state, then run health and fixture-replay checks.

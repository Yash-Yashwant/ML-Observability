# F1 Telemetry Observability Platform

Real-time backend platform to ingest Formula 1 race data, compute performance signals, and serve low-latency APIs for live and historical analysis.

## Project Goal

Build a production-style telemetry and analytics system that demonstrates:
- Real-time event ingestion
- Reliable data modeling in PostgreSQL
- Fast API serving for dashboard consumption
- Observability-first engineering (latency, freshness, correctness)

## Why This Project

This aligns with backend and infrastructure strengths:
- FastAPI + PostgreSQL + SQLAlchemy
- Real-time ingestion and monitoring patterns
- Measurable system performance outcomes

## MVP Scope

1. **Ingestion Service**
- Consume F1 event stream (laps, sectors, pits, flags, weather).
- Normalize events into canonical schema.
- Use idempotency keys to prevent duplicate writes.

2. **Core Data Model**
- `race_sessions`
- `drivers`
- `laps`
- `sectors`
- `stints`
- `pit_events`
- `weather_snapshots`
- `ingestion_events` (audit trail)

3. **Metrics Pipeline**
- Rolling lap pace deltas
- Tire degradation proxy by stint
- Pit stop impact and rank changes
- Anomaly flags (sudden pace drop, outlier sector)

4. **API Layer**
- `GET /health`
- `GET /sessions/{session_id}/leaderboard/live`
- `GET /drivers/{driver_id}/timeline`
- `GET /sessions/{session_id}/metrics`
- `GET /sessions/{session_id}/anomalies`

5. **Frontend (later stage)**
- Live leaderboard
- Event timeline
- Driver detail panel
- Race trend overlays

## Non-Functional Targets

- Ingestion P95 latency: `< 200ms`
- API P95 latency: `< 150ms`
- Freshness lag: `< 2s`
- Duplicate write rate: `0`
- Availability during race windows: `99%+`

## Proposed Repo Direction

Current repository has starter files only. Use this target layout:

```text
api/
  app.py
  routes/
database/
  connection.py
  models.py
  migrations/
services/
  ingest/
  metrics/
  jobs/
tests/
  api/
  services/
```

## 4-Week Build Plan

### Week 1: Foundation
- Secure env setup (`.env` ignored, `.env.example` committed)
- Package-safe imports
- SQLAlchemy models and initial schema migration
- Health endpoint and basic app wiring

### Week 2: Ingestion
- Stream adapter and event normalizer
- Idempotent writes and retry handling
- Ingestion audit logging

### Week 3: Metrics + API
- Aggregation jobs (rolling pace, stint metrics)
- Leaderboard and driver timeline endpoints
- Basic caching for frequently-read endpoints

### Week 4: Reliability + Demo
- Metrics dashboards (ingestion lag, API latency)
- Backfill tooling for historical sessions
- Demo workflow for one full race replay

## Immediate Next Tasks

1. Rename and clean module files (e.g., `api/fastAPI-test.py` -> `api/app.py`).
2. Fix import safety (`database/manage.py` package imports).
3. Add root `.gitignore` and remove sensitive env tracking.
4. Add first smoke tests for API startup and DB model import.

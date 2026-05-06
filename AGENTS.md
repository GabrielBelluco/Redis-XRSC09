# AGENTS.md

## Commands
- Redis: `docker compose up -d`
- Install deps: `pip install -r requirements.txt` (only `redis`)
- Calc worker: `python Server/calc_worker.py`
- Message worker: `python Server/message_worker.py`
- File worker (single instance): `python Server/file_worker.py`
- DLQ monitor: `python Server/dlq_monitor.py`
- Client: `python Client/Client.py`

## Architecture (Redis Streams)
- `requests_stream`: client XADD; workers XREADGROUP by operation
- `responses_stream`: workers XADD; client XREADGROUP by request_id
- `dead_letter_stream`: messages failing after 3 retries
- Consumer groups: `calc_group`, `message_group`, `file_group`, `client_group`
- Idempotency: 30s window via Redis SETNX (`idempotency:{request_id}`)
- Retry: XAUTOCLAIM reclaims idle entries (30s); max 3 retries → DLQ

## Gotchas
- Directory names are capitalized: `Server/` and `Client/` (README uses lowercase)
- Redis host hardcoded to `localhost:6379` in all entrypoints
- File worker is designed for single-instance execution (no distributed lock)
- No tests, linting, or typechecking configured
- `arquivo_servidor.txt` is gitignored, created at runtime

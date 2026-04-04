# NetAuto Hybrid Platform

A full working base project for a lab-style network automation platform with:

- FastAPI API layer
- CLI layer
- Celery + Redis queue
- Nornir orchestration
- Hybrid executor:
  - NAPALM for structured operations (`get_facts`, `get_interfaces`, `get_bgp_neighbors`)
  - Netmiko for arbitrary CLI commands
- Pluggable parser dispatcher
- Docker + docker-compose

## High-level flow

CLI / API -> FastAPI -> Service Layer -> Celery -> Worker -> Nornir ->
Decision Engine -> NAPALM or Netmiko -> Parser Dispatcher -> JSON Result

## Project tree

```text
netauto_full_project/
├── app/
│   ├── api/routes.py
│   ├── core/config.py
│   ├── core/celery_app.py
│   ├── main.py
│   ├── models/schemas.py
│   ├── services/job_service.py
│   └── tasks/run_commands.py
├── cli/cli.py
├── executor/
│   ├── decision_engine.py
│   ├── napalm_runner.py
│   ├── netmiko_runner.py
│   └── nornir_runner.py
├── inventory/
│   ├── defaults.yaml
│   ├── groups.yaml
│   ├── hosts.yaml
│   └── nornir_config.yaml
├── parsers/
│   ├── dispatcher.py
│   ├── genie_parser.py
│   ├── raw_parser.py
│   ├── textfsm_parser.py
│   └── ttp_parser.py
├── docker/
│   ├── Dockerfile
│   ├── celery-start.sh
│   └── api-start.sh
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

API docs:
- http://127.0.0.1:8000/docs

## Quick test (mock mode)

Submit job:
```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["show version", "get_facts"],
    "parser": "raw",
    "mock": true,
    "inventory": {"hosts": ["R1", "R2"]}
  }'
```

Then:
```bash
curl http://127.0.0.1:8000/status/<job_id>
curl http://127.0.0.1:8000/result/<job_id>
```

## CLI examples

```bash
python -m cli.cli run --command "show version" --host R1
python -m cli.cli run --command get_facts --host R1 --real
python -m cli.cli status <job_id>
python -m cli.cli result <job_id>
```

## Notes

- `mock=true` lets you test the full pipeline without real devices.
- `parser=auto` currently chooses parsers by simple rules and falls back to raw.
- Genie parser is included as a placeholder in this base project because `pyATS/Genie`
  has heavier dependency needs; you can wire it later if you want.
- For real devices, update `inventory/hosts.yaml` with valid credentials and platforms.

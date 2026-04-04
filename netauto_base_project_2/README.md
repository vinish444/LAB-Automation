# NetAuto Base Project

A working base project for a lab-style network automation platform with:
- FastAPI API layer
- CLI layer
- Celery queue
- Redis broker/result backend
- Nornir orchestration
- Netmiko execution path
- Pluggable parsing layer
- Docker and Docker Compose support

## 1. Project layout

```text
netauto_base_project/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── tasks/
├── cli/
├── executor/
├── parsers/
├── nornir_config/
├── docker/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 2. What each layer does

- **CLI layer**: user-friendly terminal commands
- **API layer**: receives HTTP requests
- **Service layer**: prepares the job payload
- **Queue layer**: Celery + Redis manage jobs across requests
- **Worker layer**: Celery workers pick queued jobs
- **Orchestration layer**: Nornir handles per-job host filtering and parallelism
- **Execution layer**: Netmiko runs CLI commands when `mock=false`
- **Parsing layer**: raw parser or placeholder TextFSM parser

## 3. Quick local run (without Docker)

### Start Redis

Ubuntu:

```bash
sudo apt update
sudo apt install -y redis-server
sudo systemctl start redis-server
```

### Create venv and install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Start API

```bash
uvicorn app.main:app --reload
```

### Start worker in another terminal

```bash
celery -A app.tasks.run_commands worker --loglevel=info
```

## 4. Test from Swagger

Open:
- `http://127.0.0.1:8000/docs`

Submit a request to `/run`:

```json
{
  "command": "show version",
  "parser": "raw",
  "mock": true,
  "inventory": {
    "hosts": ["r1", "nr1"]
  }
}
```

Then use the returned `job_id` with:
- `GET /status/{job_id}`
- `GET /result/{job_id}`

## 5. Test from CLI

Submit job:

```bash
python cli/cli.py run --command "show version" --host r1
```

Check status:

```bash
python cli/cli.py status <job_id>
```

Get result:

```bash
python cli/cli.py result <job_id>
```

## 6. Real device mode

By default, the base project runs in **mock mode** so you can validate the full architecture without real devices.

To use real SSH:
1. Update `nornir_config/hosts.yaml`
2. Update usernames/passwords in inventory
3. Submit with `mock=false` in API, or `--real` in CLI

Example API payload:

```json
{
  "command": "show ip interface brief",
  "parser": "raw",
  "mock": false,
  "inventory": {
    "groups": ["lab"]
  }
}
```

## 7. Docker Compose run

```bash
docker compose up --build
```

Services:
- API: `http://127.0.0.1:8000`
- Redis: `localhost:6379`
- Celery worker: background execution

## 8. Important notes

- This is a **base project**, intentionally simple and clean.
- The TextFSM parser is a placeholder dispatcher so you can later plug in `ntc-templates`.
- Genie and TTP can be added later into the same `parsers/dispatcher.py` pattern.
- NAPALM can be added later as another executor module.

## 9. Suggested next enhancements

- Add job history in PostgreSQL
- Add Redis job progress updates
- Add parser selection for Genie and TTP
- Add device grouping by region / DC / building
- Add logging per host
- Add retries and timeout policies
- Add authentication for the API

# NetAuto Vault + Template Reference Platform

This project is a complete working starter for a Dockerized network automation platform that combines:

- FastAPI API layer
- CLI layer
- Celery + Redis job execution
- Nornir orchestration
- Netmiko + NAPALM execution routing
- Parser selection driven by YAML maps
- Template reference logic for TextFSM and TTP
- HashiCorp Vault credential lookup using AppRole
- Docker Compose with secret-file based runtime injection

## What was added on top of the base project

1. **Vault AppRole integration**
   - Centralized Vault client in `app/core/vault_client.py`
   - Reads `role_id` and `secret_id` from Docker secret files or environment variables
   - Supports wrapped SecretID file if you want response-wrapping later
   - Injects credentials into Nornir inventory before real execution

2. **Template reference + parser mapping design**
   - `data/command_map.yaml` maps user intent to platform-specific commands
   - `data/parser_map.yaml` maps platform+command to parser and template file
   - `templates/textfsm/custom/` contains custom template examples
   - `templates/ttp/` contains TTP example templates
   - `NET_TEXTFSM` can point to an NTC templates checkout if you want the standard library

3. **Production-friendly flow**
   - User/API sends command or intent such as `interface_status`
   - Project resolves actual platform command
   - Project selects parser using YAML
   - Project uses Vault credentials for real device access
   - Parsed output is returned as JSON

## Architecture

```text
CLI / API
   ↓
FastAPI route
   ↓
Celery task
   ↓
Nornir filtered inventory
   ↓
Vault credential injection (real mode)
   ↓
command_map.yaml → resolve real command
   ↓
decision_engine.py → NAPALM or Netmiko
   ↓
parser_map.yaml → parser + template selection
   ↓
TextFSM / TTP / Genie placeholder / raw
   ↓
JSON result
```

## Project tree

```text
netauto_vault_project/
├── app/
│   ├── api/
│   ├── core/
│   │   ├── celery_app.py
│   │   ├── config.py
│   │   └── vault_client.py
│   ├── models/
│   ├── services/
│   ├── tasks/
│   └── utils/
├── cli/
├── data/
│   ├── command_map.yaml
│   ├── parser_map.yaml
│   └── vault_roles.yaml
├── docker/
├── executor/
├── inventory/
├── parsers/
│   ├── dispatcher.py
│   ├── selector.py
│   ├── textfsm_parser.py
│   ├── ttp_parser.py
│   └── ...
├── secrets/
│   ├── vault_role_id
│   └── vault_secret_id
├── templates/
│   ├── textfsm/custom/
│   └── ttp/
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Important design note on templates

This project supports the exact model you were asking for:

- **Genie**: parser-only model for supported Cisco commands
- **TextFSM**: template-driven parsing
- **TTP**: template-driven parsing
- **Raw**: safe fallback when nothing is mapped

The idea is:

- keep standard templates outside your code if you want, such as NTC templates
- keep only enterprise-specific or missing templates inside `templates/textfsm/custom/`
- use YAML mapping so the code does not hardcode every vendor/command case

## How command/template selection works

### `data/command_map.yaml`
Maps a logical intent to the real command by platform.

Example:

```yaml
intents:
  interface_status:
    cisco_ios: show ip interface brief
    juniper_junos: show interfaces terse
```

### `data/parser_map.yaml`
Maps the real command to a parser and optional template.

Example:

```yaml
platforms:
  cisco_ios:
    show ip interface brief:
      parser: textfsm
      template: cisco_ios_show_ip_interface_brief.textfsm
```

This lets you keep one API contract while still supporting different vendor commands and templates.

## Vault credential model

### Expected Vault secrets
By default the app expects secrets like:

- `kv/network-automation/cisco/shared`
- `kv/network-automation/arista/shared`
- `kv/network-automation/juniper/shared`

With fields such as:

```json
{
  "username": "svc_netauto",
  "password": "super-secret"
}
```

You can change secret paths and field names in `data/vault_roles.yaml`.

## AppRole input options

The project supports these patterns, in this order:

1. `VAULT_TOKEN` if you explicitly use a token
2. `VAULT_ROLE_ID` and `VAULT_SECRET_ID` environment variables
3. `VAULT_ROLE_ID_FILE` and `VAULT_SECRET_ID_FILE`
4. `VAULT_WRAPPED_SECRET_ID_FILE` for response-wrapped SecretID flow

## Recommended secure runtime pattern

For containerized production:

- pass `role_id` and `secret_id` as mounted files or orchestrator secrets
- avoid baking any Vault credential into the image
- prefer a short-lived or wrapped SecretID delivery flow
- let Vault return the runtime token after AppRole login

## Quick start

### 1. Prepare environment

```bash
cp .env.example .env
```

### 2. Put your AppRole IDs into secret files

```bash
printf 'your-role-id' > secrets/vault_role_id
printf 'your-secret-id' > secrets/vault_secret_id
```

### 3. Run the stack

```bash
docker compose up --build
```

API docs:

- http://127.0.0.1:8000/docs

## Mock-mode testing

Mock mode is enabled by default, so you can test without real devices and without Vault.

### API example

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["interface_status", "version"],
    "parser": "auto",
    "mock": true,
    "inventory": {"hosts": ["R1", "R2"]}
  }'
```

### CLI example

```bash
python -m cli.cli run --command interface_status --command version --host R1
```

## Real execution example

```bash
python -m cli.cli run \
  --command interface_status \
  --host R1 \
  --real
```

In real mode, the app will:

1. authenticate to Vault
2. read platform-specific secret path
3. inject credentials into Nornir host objects
4. connect to devices
5. parse output according to YAML mapping

## NTC templates usage

This project does **not** vendor the whole NTC templates repository.

You have two normal ways to use it:

### Option A: install package or checkout repo externally
Point `NET_TEXTFSM` to the templates directory.

Example:

```bash
export NET_TEXTFSM=/path/to/ntc-templates/ntc_templates/templates
```

### Option B: place enterprise-only templates locally
Put only custom or missing templates in:

```text
templates/textfsm/custom/
```

## Files you will likely customize first

- `data/command_map.yaml`
- `data/parser_map.yaml`
- `data/vault_roles.yaml`
- `inventory/hosts.yaml`
- `.env`
- `templates/textfsm/custom/*`
- `templates/ttp/*`

## Notes

- Genie is still kept as an integration point instead of bundling the full pyATS stack into this base image.
- The mock Netmiko runner includes sample outputs so TextFSM and TTP templates can be demonstrated immediately.
- If you want, you can later split Vault login into a sidecar/agent pattern instead of direct `hvac` login from the app.

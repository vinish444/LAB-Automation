from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    nornir_config_file: str = "inventory/nornir_config.yaml"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    vault_addr: str = "http://localhost:8200"
    vault_namespace: str = ""
    vault_kv_mount: str = "kv"
    vault_kv_version: str = "v2"
    vault_secret_path: str = "network-automation/service-account"
    vault_role_id_file: str = ""
    vault_secret_id_file: str = ""
    vault_wrapped_secret_id_file: str = ""
    vault_role_id: str = ""
    vault_secret_id: str = ""
    vault_token: str = ""
    vault_auth_mode: str = "approle"
    vault_verify: bool = True
    vault_timeout: int = 10

    net_textfsm: str = ""
    parser_map_file: str = "data/parser_map.yaml"
    command_map_file: str = "data/command_map.yaml"
    vault_role_map_file: str = "data/vault_roles.yaml"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import hvac
import yaml

from app.core.config import settings


@dataclass
class VaultCredential:
    username: str
    password: str
    source_path: str


class VaultError(RuntimeError):
    pass


class VaultClientManager:
    def __init__(self) -> None:
        self._client: Optional[hvac.Client] = None
        self._role_map: Optional[Dict[str, Any]] = None
        self._cache: Dict[str, VaultCredential] = {}

    def _read_file(self, path_value: str) -> str:
        if not path_value:
            return ""
        path = Path(path_value)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8").strip()

    def _build_client(self) -> hvac.Client:
        client = hvac.Client(
            url=settings.vault_addr,
            namespace=settings.vault_namespace or None,
            verify=settings.vault_verify,
            timeout=settings.vault_timeout,
        )
        return client

    def _authenticate(self, client: hvac.Client) -> None:
        if settings.vault_token:
            client.token = settings.vault_token
            return

        mode = (settings.vault_auth_mode or "approle").lower()
        if mode != "approle":
            raise VaultError(f"Unsupported vault auth mode: {mode}")

        role_id = settings.vault_role_id or self._read_file(settings.vault_role_id_file)
        secret_id = settings.vault_secret_id or self._read_file(settings.vault_secret_id_file)
        wrapped_secret = self._read_file(settings.vault_wrapped_secret_id_file)

        if wrapped_secret and not secret_id:
            unwrap_response = client.sys.unwrap(token=wrapped_secret)
            if not isinstance(unwrap_response, dict) or "secret_id" not in unwrap_response.get("data", {}):
                raise VaultError("Wrapped SecretID was provided but Vault did not return secret_id")
            secret_id = unwrap_response["data"]["secret_id"]

        if not role_id or not secret_id:
            raise VaultError(
                "Vault AppRole authentication requires role_id and secret_id. "
                "Provide them through files or environment variables."
            )

        client.auth.approle.login(role_id=role_id, secret_id=secret_id)

    def get_client(self) -> hvac.Client:
        if self._client is None:
            client = self._build_client()
            self._authenticate(client)
            if not client.is_authenticated():
                raise VaultError("Vault authentication failed")
            self._client = client
        return self._client

    def _load_role_map(self) -> Dict[str, Any]:
        if self._role_map is None:
            with open(settings.vault_role_map_file, "r", encoding="utf-8") as handle:
                self._role_map = yaml.safe_load(handle) or {}
        return self._role_map

    def _mapping_for_platform(self, platform: str) -> Dict[str, Any]:
        role_map = self._load_role_map()
        defaults = role_map.get("default", {})
        platform_map = (role_map.get("platforms") or {}).get(platform, {})
        merged = dict(defaults)
        merged.update(platform_map)
        return merged

    def read_credentials(self, platform: str) -> VaultCredential:
        if platform in self._cache:
            return self._cache[platform]

        mapping = self._mapping_for_platform(platform)
        secret_path = mapping.get("secret_path") or settings.vault_secret_path
        username_field = mapping.get("username_field", "username")
        password_field = mapping.get("password_field", "password")

        client = self.get_client()
        if settings.vault_kv_version.lower() == "v1":
            secret_response = client.secrets.kv.v1.read_secret(
                path=secret_path,
                mount_point=settings.vault_kv_mount,
            )
            data = secret_response.get("data", {})
        else:
            secret_response = client.secrets.kv.v2.read_secret_version(
                path=secret_path,
                mount_point=settings.vault_kv_mount,
            )
            data = secret_response.get("data", {}).get("data", {})

        username = data.get(username_field)
        password = data.get(password_field)
        if not username or not password:
            raise VaultError(
                f"Vault secret '{secret_path}' does not contain fields '{username_field}' and '{password_field}'"
            )

        cred = VaultCredential(username=username, password=password, source_path=secret_path)
        self._cache[platform] = cred
        return cred


vault_manager = VaultClientManager()

#!/bin/sh
set -eu

echo "Vault Agent Entrypoint Starting..."
echo "VAULT_ADDR=$VAULT_ADDR"

# Write role_id
printf '%s' "$ROLE_ID" > /tmp/role_id

echo "Unwrapping Secret ID..."

# Unwrap wrapped token
SECRET_JSON=$(vault unwrap -format=json "$WRAP_TOKEN" || true)

echo "$SECRET_JSON"

SECRET_ID=$(printf '%s' "$SECRET_JSON" | jq -r '.data.secret_id')

# Validate secret_id
if [ -z "$SECRET_ID" ] || [ "$SECRET_ID" = "null" ]; then
  echo "ERROR: secret_id extraction failed"
  exit 1
fi

printf '%s' "$SECRET_ID" > /tmp/secret_id

echo "secret_id written successfully"

echo "Starting Vault Agent..."
exec vault agent -config=/vault-agent/config.hcl
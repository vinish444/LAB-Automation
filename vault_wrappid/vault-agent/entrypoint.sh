#!/bin/sh

echo "$ROLE_ID" > /tmp/role_id

SECRET_JSON=$(vault unwrap -format=json $WRAP_TOKEN)
SECRET_ID=$(echo $SECRET_JSON | sed -n 's/.*"secret_id":"\([^"]*\)".*/\1/p')

echo "$SECRET_ID" > /tmp/secret_id

vault agent -config=/vault-agent/config.hcl &
sleep 3

rm -f /tmp/secret_id

wait

FROM hashicorp/vault:1.15

RUN apk add --no-cache jq

COPY vault-agent /vault-agent

# ❌ REMOVE THESE (IMPORTANT)
# RUN chmod +x /vault-agent/entrypoint.sh
# ENTRYPOINT ["/vault-agent/entrypoint.sh"]
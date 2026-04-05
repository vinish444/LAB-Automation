pid_file = "/tmp/vault-agent.pid"

vault {
  address = "http://host.docker.internal:8200"
}

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path   = "/vault/bootstrap/role_id"
      secret_id_file_path = "/vault/bootstrap/secret_id"
    }
  }

  sink "file" {
    config = {
      path = "/shared/vault-token"
    }
  }
}

# 🔥 THIS CREATES YOUR JSON FILE
template {
  source      = "/vault/template/template.ctmpl"
  destination = "/vault/secrets/device.json"
}

listener "tcp" {
  address = "0.0.0.0:8100"
  tls_disable = true
}

cache {
  use_auto_auth_token = true
}
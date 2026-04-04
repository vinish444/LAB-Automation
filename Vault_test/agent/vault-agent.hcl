pid_file = "/tmp/vault-agent.pid"

vault {
  address = "http://vault:8200"
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
      path = "/vault/token"
    }
  }
}

template {
  source      = "/vault/template/template.ctmpl"
  destination = "/vault/secrets/device.json"
}

cache {
  use_auto_auth_token = true
}

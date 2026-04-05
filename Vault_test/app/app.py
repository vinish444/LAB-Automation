import time
import json
from pathlib import Path

FILE = "/vault/secrets/device.json"

print("🚀 App started... waiting for secret...")

while True:
    try:
        data = json.loads(Path(FILE).read_text())
        print("\n🔥 Got credentials from Vault:")
        print(f"Username: {data['username']}")
        print(f"Password: {data['password']}")
        break
    except Exception:
        print("⏳ Waiting for Vault Agent...")
        time.sleep(2)
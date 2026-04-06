import json
import time
import os

FILE = "/vault/secrets/device.json"

print("App started...")

while not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
    print("Waiting for secret file...")
    time.sleep(1)

with open(FILE) as f:
    data = json.load(f)

print("Secrets:")
print(data)
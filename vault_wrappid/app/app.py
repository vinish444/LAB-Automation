
import json, time

while True:
    try:
        with open("/vault/secrets/device.json") as f:
            print("Secrets:", json.load(f))
    except Exception as e:
        print("Waiting...", e)
    time.sleep(5)

import json
import requests

def send_webhook(payload: dict, url: str):
    headers = {
        "Content-Type": "apllication/json"
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response
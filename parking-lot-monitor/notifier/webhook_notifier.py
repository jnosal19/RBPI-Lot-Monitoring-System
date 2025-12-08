# notifier/webhook_notifier.py

import requests
import json
from notifier.base import Notifier
from config import WEBHOOK_URL

class WebhookNotifier(Notifier):
    def __init__(self):
        if not WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL is empty.")
        self.url = WEBHOOK_URL

    def send(self, title, message, image_path=None):
        try:
            if image_path:
                # Send with image attachment
                with open(image_path, "rb") as f:
                    payload = {
                        "content": f"**{title}**\n{message}"
                    }
                    files = {
                        "file": (image_path.split("/")[-1], f, "image/jpeg")
                    }
                    response = requests.post(
                        self.url,
                        data={"payload_json": json.dumps(payload)},
                        files=files
                    )
            else:
                # Send text only
                payload = {
                    "content": f"**{title}**\n{message}"
                }
                response = requests.post(self.url, json=payload)
            
            # Check response
            if response.status_code == 204 or response.status_code == 200:
                print(f"✓ Discord notification sent successfully")
            else:
                print(f"✗ Discord error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"✗ Failed to send Discord notification: {e}")

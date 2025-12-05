# notifier/webhook_notifier.py

import requests
from notifier.base import Notifier
from config import WEBHOOK_URL

class WebhookNotifier(Notifier):
    def __init__(self):
        if not WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL is empty.")
        self.url = WEBHOOK_URL

    def send(self, title, message, image_path=None):
        data = {
            "content": f"**{title}**\n{message}"
        }

        if image_path:
            files = {"file": open(image_path, "rb")}
            payload = {"payload_json": str(data)}
            requests.post(self.url, data=payload, files=files)
        else:
            requests.post(self.url, json=data)

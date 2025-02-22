from venv import logger
import requests
from django.conf import settings

def send_webhook_notification(contact_id):
    webhook_urls = settings.WEBHOOK_ENDPOINTS
    for url in webhook_urls:
        try:
            requests.post(
                url,
                json={'contact_id': contact_id, 'event': 'contact_updated'},
                timeout=2
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook failed for {url}: {str(e)}")
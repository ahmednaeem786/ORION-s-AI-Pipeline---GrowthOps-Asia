import logging

import requests

from schemas import ReviewerPayload

logger = logging.getLogger(__name__)

class ReviewAPIClient:
    """Dispatches validated reviewer payloads to an external downstream API."""

    def __init__(self, endpoint_url: str = "https://httpbin.org/post"):
        self.endpoint_url = endpoint_url
        # Mock API Key

    def emit_result(self, payload: ReviewerPayload) -> bool:
        """Sends the structured payload via HTTP POST with status checking."""
        logger.info(f"Emitting payload for {payload.submission_id} to {self.endpoint_url}")

        payload_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-System-Origin": "ORION-AI-Pipeline",
            "X-Submission-ID": payload.submission_id,
            # "X-Submission-Timestamp": payload.submission_timestamp,
            "X-Risk-Tier": payload.recommended_authorization_level.replace(" ", "-")
        }
        
        try:
            # We use httpbin.org/post as a live mirror endpoint for testing,
            # or mock the call if no network is desired.
            response = requests.post(
                self.endpoint_url,
                json=payload.model_dump(),
                headers=payload_headers,
                timeout=10
            )
            
            if response.status_code in (200, 201):
                logger.info(f"Successfully delivered payload for {payload.submission_id} (HTTP {response.status_code}).")
                return True
            else:
                logger.warning(f"Failed delivery with status code: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error emitting payload to review API: {e}")
            return False
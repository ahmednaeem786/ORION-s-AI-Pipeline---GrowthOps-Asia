import logging
import requests
from schemas import ReviewerPayload

logger = logging.getLogger(__name__)

class ReviewAPIClient:
    """Dispatches validated reviewer payloads to an external downstream API."""

    def __init__(self, endpoint_url: str = "https://httpbin.org/post"):
        self.endpoint_url = endpoint_url

    def emit_result(self, payload: ReviewerPayload) -> bool:
        """Sends the structured payload via HTTP POST with status checking."""
        logger.info(f"Emitting payload for {payload.submission_id} to {self.endpoint_url}")
        
        try:
            # We use httpbin.org/post as a live mirror endpoint for testing,
            # or mock the call if no network is desired.
            response = requests.post(
                self.endpoint_url,
                json=payload.model_dump(),
                headers={"Content-Type": "application/json"},
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
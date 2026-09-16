import logging
import os

import requests

from .schemas import ReviewerPayload


logger = logging.getLogger(__name__)


class ReviewAPIClient:
    """Dispatches validated reviewer payloads to an external downstream API."""

    def __init__(self, endpoint_url: str = "https://httpbin.org/post"):
        self.endpoint_url = endpoint_url
        # Mock API Key for testing; in production, this should be set in the environment
        self.api_key = os.environ.get("REVIEW_API_KEY", "mock-api-key")

    def emit_result(self, payload: ReviewerPayload) -> bool:
        """Sends the structured payload via HTTP POST with status checking."""
        logger.info(
            f"Emitting payload for {payload.submission_id} to {self.endpoint_url}"
        )

        payload_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-System-Origin": "ORION-AI-Pipeline",
            "X-Submission-ID": payload.submission_id,
            "X-Submission-Timestamp": payload.submission_timestamp,
            "X-Risk-Tier": payload.recommended_authorization_level.replace(" ", "-"),
        }

        try:
            # We use httpbin.org/post as a live mirror endpoint for testing,
            # or mock the call if no network is desired.
            response = requests.post(
                self.endpoint_url,
                json=payload.model_dump(),
                headers=payload_headers,
                timeout=10,
            )

            if response.status_code in (200, 201):
                logger.info(
                    f"Successfully delivered payload for {payload.submission_id} (HTTP {response.status_code})."
                )
                return True
            else:
                logger.warning(
                    f"Failed delivery. Target API rejected the payload with status code: {response.status_code}. Response: {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            logger.error(
                f"Timeout Error: The external API at {self.endpoint_url} took longer than 10 seconds to respond. Consider implementing a retry backoff."
            )
            return False

        except requests.exceptions.ConnectionError:
            logger.error(
                f"Connection Error: Failed to establish a connection to {self.endpoint_url}. Please verify network connectivity and DNS resolution."
            )
            return False

        except requests.exceptions.RequestException as e:
            # Catches any other requests-related errors (e.g., TooManyRedirects, InvalidSchema)
            logger.error(
                f"HTTP Request Error: An unexpected network issue occurred. Details: {e}"
            )
            return False

        except Exception as e:
            # The final safety net for purely systemic Python errors (e.g., memory overflow)
            logger.error(
                f"System Error: A critical internal error occurred during payload emission. Details: {e}"
            )
            return False

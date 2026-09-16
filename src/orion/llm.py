import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from .schemas import DimensionRisk

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Suppress the Google GenAI SDK's AFC warning while preserving API errors.
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

RETRYABLE_MODEL_ERRORS = (
    "429",
    "500",
    "502",
    "503",
    "504",
    "DEADLINE_EXCEEDED",
    "RESOURCE_EXHAUSTED",
    "UNAVAILABLE",
)


class RiskExtraction(BaseModel):
    """Wrapper schema to force the LLM to return a list of DimensionRisks."""

    extracted_risks: list[DimensionRisk] = Field(
        ...,
        description="List of risk assessments across the required regulatory dimensions.",
    )


class LLMEngine:
    """Handles prompt construction and structured API calls to the LLM."""

    def __init__(
        self,
        model_name: str = "gemini-3.6-flash",
        fallback_models: list[str] | None = None,
    ):
        # The genai.Client automatically picks up GEMINI_API_KEY from the environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Set it in .env or the process environment."
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model_name
        self.fallback_models = list(
            fallback_models
            if fallback_models is not None
            else ["gemini-3.8-flash", "gemini-3.5-flash"]
        )

    def extract_risks(self, text: str, company_name: str) -> list[DimensionRisk]:
        """Evaluates the text and extracts structured risk dimensions."""
        logger.info(
            f"Sending {len(text)} characters to {self.model} for {company_name}."
        )

        system_instruction = (
            f"You are a regulatory compliance AI assisting an analyst at ORION. "
            f"Review the provided SEC 10-K Risk Factors section for {company_name}. "
            f"Evaluate the company strictly across these four dimensions:\n"
            f"1. Operational Resilience\n"
            f"2. Regulatory Integrity\n"
            f"3. Financial Solvency\n"
            f"4. Data Security\n\n"
            f"For each dimension, extract the following:\n"
            f"- risk_level: Assign 'Low', 'Medium', or 'High'.\n"
            f"- rationale: Explain your reasoning for this severity.\n"
            f"- evidence: Provide a concise, exact quote from the text as proof.\n"
            f"- mitigating_controls: Extract any defenses or fixes the company claims to have in place for this risk. "
            f"If a dimension is not discussed, assign 'Low' and state 'No explicit risks found in the provided text'."
        )

        models_to_try = [self.model, *self.fallback_models]
        for model_index, model in enumerate(models_to_try):
            if model_index > 0:
                logger.info("Trying fallback model: %s", model)

            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        response_schema=RiskExtraction,
                    ),
                )
                result = response.parsed
                logger.info(
                    "Successfully extracted %s risk dimensions using %s.",
                    len(result.extracted_risks),
                    model,
                )
                return result.extracted_risks
            except Exception as error:
                is_retryable = any(
                    marker in str(error) for marker in RETRYABLE_MODEL_ERRORS
                )
                if model_index == 0 and not is_retryable:
                    logger.error("LLM extraction failed: %s", error)
                    raise
                logger.warning("Model %s failed: %s", model, error)

        raise RuntimeError("LLM extraction failed on all configured models.")


if __name__ == "__main__":
    try:
        with open("data/raw/extracted_item_1a.txt", "r", encoding="utf-8") as f:
            sample_text = f.read()

        engine = LLMEngine()
        risks = engine.extract_risks(sample_text, "Coinbase Global, Inc.")

        print("\n--- LLM EXTRACTION RESULTS ---")
        for risk in risks:
            print(f"\nDimension: {risk.dimension_name}")
            print(f"Risk Level: {risk.risk_level}")
            print(f"Evidence: {risk.evidence}")

    except Exception as e:
        print(f"Test failed: {e}")

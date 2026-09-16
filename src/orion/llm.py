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


class RiskExtraction(BaseModel):
    """Wrapper schema to force the LLM to return a list of DimensionRisks."""

    extracted_risks: list[DimensionRisk] = Field(
        ...,
        description="List of risk assessments across the required regulatory dimensions.",
    )


class LLMEngine:
    """Handles prompt construction and structured API calls to the LLM."""

    def __init__(self, model_name: str = "gemini-3.6-flash"):
        # The genai.Client automatically picks up GEMINI_API_KEY from the environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Set it in .env or the process environment."
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model_name

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
            f"For each dimension, assign a risk_level ('Low', 'Medium', 'High') and extract a concise "
            f"quote directly from the text as 'evidence'. Do not invent information. If a dimension "
            f"is not discussed, assign 'Low' and state 'No explicit risks found in the provided text'."
        )

        try:
            # The SDK natively forces the LLM to output JSON matching the Pydantic schema
            response = self.client.models.generate_content(
                model=self.model,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=RiskExtraction,
                ),
            )

            # The google-genai SDK automatically parses the JSON back into your Pydantic model
            result = response.parsed
            logger.info(
                f"Successfully extracted {len(result.extracted_risks)} risk dimensions."
            )
            return result.extracted_risks

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            raise


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

import json
import logging
import time
from schemas import SubmissionInput, ReviewerPayload
from parser import DocumentParser
from llm import LLMEngine
from scoring import RiskScorer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OrionPipeline:
    """
    Main orchestration pipeline for the ORION authorization review workflow.
    """

    def __init__(self, llm_model: str = "gemini-3.6-flash"):
        self.parser = DocumentParser()
        self.llm = LLMEngine(model_name=llm_model)
        self.scorer = RiskScorer()

    def process_submission(self, submission_file: str) -> ReviewerPayload:
        start_time = time.time()
        logger.info(f"Starting pipeline execution for submission file: {submission_file}")

        # 1. Ingest & validate submission JSON against schema
        with open(submission_file, "r", encoding="utf-8") as f:
            raw_json = json.load(f)
        
        submission_data = SubmissionInput(**raw_json)
        logger.info(f"Ingested submission ID: {submission_data.submission_id} for applicant: {submission_data.applicant.company_name}")

        # 2. Ingest referenced document (abstracting local file path or cloud URI)
        # We take the primary document referenced
        doc_uri = submission_data.document_uris[0]
        resolved_path = doc_uri.replace("local://", "")

        # 3. Parse & filter high-density risk text
        extracted_text = self.parser.process_document(resolved_path)

        # 4. LLM reasoning and extraction
        dimension_risks = self.llm.extract_risks(
            text=extracted_text, 
            company_name=submission_data.applicant.company_name
        )

        # 5. Deterministic scoring and decision synthesis
        composite_score = self.scorer.calculate_composite_score(dimension_risks)
        auth_level = self.scorer.determine_authorization_level(composite_score)
        follow_ups = self.scorer.generate_follow_ups(dimension_risks)

        # 6. Assemble output payload validated against Pydantic schema
        output_payload = ReviewerPayload(
            submission_id=submission_data.submission_id,
            dimension_risks=dimension_risks,
            composite_score=composite_score,
            recommended_authorization_level=auth_level,
            follow_up_questions=follow_ups
        )

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"Pipeline finished for {submission_data.submission_id} in {elapsed}s with authorization verdict: '{auth_level}'.")
        return output_payload

if __name__ == "__main__":
    # Test end-to-end execution
    pipeline = OrionPipeline()
    result = pipeline.process_submission("data/mock_input/submission_coinbase.json")
    
    print("\n=======================================================")
    print("FINAL REVIEWER PAYLOAD (Emitted for Human Review)")
    print("=======================================================")
    print(result.model_dump_json(indent=2))
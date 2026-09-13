from schemas import DimensionRisk
import logging

logger = logging.getLogger(__name__)

# Numeric mapping for risk levels
RISK_WEIGHTS = {
    "Low": 1.0,
    "Medium": 2.5,
    "High": 5.0
}

# Dimension Weighting - equals to 1.0
DIMENSION_WEIGHTS = {
    "Operational Resilience": 0.25,
    "Regulatory Integrity": 0.35,  # Slightly higher weight for financial regulatory compliance
    "Financial Solvency": 0.20,
    "Data Security": 0.20
}

class RiskScorer:
    """
    Deterministic scoring engine to ensure explainable, auditable,
    and reproducible composite risk calculations.
    """

    @staticmethod
    def calculate_composite_score(dimension_risks: list[DimensionRisk]) -> float:
        """Calculates a weighted composite risk score between 1.0 (lowest) and 5.0 (highest)."""
        total_weight = 0.0
        weighted_sum = 0.0

        for item in dimension_risks:
            weight = DIMENSION_WEIGHTS.get(item.dimension_name, 0.25)
            numeric_score = RISK_WEIGHTS.get(item.risk_level, 3.0)
            
            weighted_sum += numeric_score * weight
            total_weight += weight

        composite = round(weighted_sum / total_weight, 2)
        logger.info(f"Calculated deterministic composite risk score: {composite}")
        return composite

    @staticmethod
    def determine_authorization_level(composite_score: float) -> str:
        """
        Maps composite risk score to recommended authorization tier:
        - 1.0 to 1.8: Full Authorization
        - 1.9 to 3.2: Conditional Authorization
        - 3.3 to 5.0: Requires Supervisory Audit / Escalated Review
        """
        if composite_score <= 1.8:
            return "Full Authorization"
        elif composite_score <= 3.2:
            return "Conditional Authorization"
        else:
            return "Requires Supervisory Audit"

    @staticmethod
    def generate_follow_ups(dimension_risks: list[DimensionRisk]) -> list[str]:
        """
        Generates targeted clarification questions for high-risk flags or gaps.
        """
        questions = []
        for item in dimension_risks:
            if item.risk_level == "High":
                if "regulatory" in item.dimension_name.lower():
                    questions.append(
                        "Provide a formal update on active regulatory proceedings and current remediation or settlement status."
                    )
                elif "security" in item.dimension_name.lower() or "data" in item.dimension_name.lower():
                    questions.append(
                        "Submit independent penetration testing reports and evidence of account recovery hardening implemented after the cited incident."
                    )
                elif "operational" in item.dimension_name.lower():
                    questions.append(
                        "Furnish secondary disaster recovery drill logs and maximum allowable downtime metrics for core transaction systems."
                    )
                elif "financial" in item.dimension_name.lower():
                    questions.append(
                        "Provide certified liquidity stress-test results under a 50% decline in trading volume scenario."
                    )

        if not questions:
            questions.append("No immediate high-risk follow-ups required. Standard periodic reporting applies.")

        return questions
from orion.schemas import DimensionRisk
from orion.scoring import RiskScorer
from orion.parser import DocumentParser


def test_risk_scorer_high():
    risks = [
        DimensionRisk(
            dimension_name="Operational Resilience",
            risk_level="High",
            rationale="A significant outage could interrupt core services.",
            evidence="Outage risk",
            mitigating_controls="None disclosed",
        ),
        DimensionRisk(
            dimension_name="Regulatory Integrity",
            risk_level="High",
            rationale="The submission references regulatory proceedings.",
            evidence="SEC lawsuit",
            mitigating_controls="None disclosed",
        ),
        DimensionRisk(
            dimension_name="Financial Solvency",
            risk_level="High",
            rationale="Market volatility could materially affect results.",
            evidence="Price drops",
            mitigating_controls="None disclosed",
        ),
        DimensionRisk(
            dimension_name="Data Security",
            risk_level="High",
            rationale="A breach could expose customer information.",
            evidence="Breach",
            mitigating_controls="None disclosed",
        ),
    ]
    score = RiskScorer.calculate_composite_score(risks)
    verdict = RiskScorer.determine_authorization_level(score, risks)

    assert score == 5.0
    assert verdict == "Requires Supervisory Audit"


def test_risk_scorer_low():
    risks = [
        DimensionRisk(
            dimension_name="Operational Resilience",
            risk_level="Low",
            evidence="Clean",
            rationale="No operational risk was identified.",
            mitigating_controls="Controls disclosed",
        ),
        DimensionRisk(
            dimension_name="Regulatory Integrity",
            risk_level="Low",
            evidence="Clean",
            rationale="No regulatory risk was identified.",
            mitigating_controls="Controls disclosed",
        ),
        DimensionRisk(
            dimension_name="Financial Solvency",
            risk_level="Low",
            evidence="Profitable",
            rationale="The company reports profitable operations.",
            mitigating_controls="Controls disclosed",
        ),
        DimensionRisk(
            dimension_name="Data Security",
            risk_level="Low",
            rationale="The available evidence indicates encryption controls.",
            evidence="Encrypted",
            mitigating_controls="Encryption disclosed",
        ),
    ]
    score = RiskScorer.calculate_composite_score(risks)
    verdict = RiskScorer.determine_authorization_level(score, risks)

    assert score == 1.0
    assert verdict == "Full Authorization"


def test_regex_parser():
    mock_raw = (
        "Table of Contents Item 1A. Risk Factors page 2\n"
        "Item 1A. Risk Factors\n"
        "Critical vulnerability detected in primary database cluster.\n"
        "Item 1B. Unresolved Staff Comments\n"
        "End of filing."
    )
    extracted = DocumentParser.extract_item_1a(mock_raw)
    assert "Critical vulnerability detected" in extracted
    assert "Table of Contents" not in extracted

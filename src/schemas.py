from pydantic import BaseModel, Field

# ==========================================
# 1. INPUT SCHEMAS (What ORION provides)
# ==========================================

class ApplicantMetadata(BaseModel):
    """The primary JSON file describing the applicant and declared activities."""
    company_name: str = Field(..., description="Legal name of the applicant firm.")
    jurisdiction: str = Field(..., description="Firm's Operating Region")
    key_executives: list[str] = Field(..., description="List of primary directors, founders, or C-Suite executives.")
    declared_activities: list[str] = Field(..., description="List of financial/digital services the firm intends to provide.")
    employee_count: int = Field(..., description="Declared number of employees.")

class SubmissionInput(BaseModel):
    """The complete payload arriving at the start of the pipeline."""
    submission_id: str = Field(..., description="Unique identifier for the application.")
    applicant: ApplicantMetadata = Field(..., description="Core details of the applicant.")
    document_uris: list[str] = Field(..., description="References to the document set held in external storage (PDF, DOCX, etc.).")


# ==========================================
# 2. OUTPUT SCHEMAS (What the pipeline delivers)
# ==========================================

class DimensionRisk(BaseModel):
    """Risk rating and evidence for a specific operational dimension."""
    dimension_name: str = Field(
        ..., 
        description="The category of risk (e.g., 'Financial Solvency', 'Operational Resilience', 'Data Security')."
    )
    risk_level: str = Field(
        ..., 
        description="The assigned risk rating. Must be 'Low', 'Medium', or 'High'."
    )
    evidence: str = Field(
        ..., 
        description="Direct quotes or specific facts extracted from the documents justifying this rating."
    )

class ReviewerPayload(BaseModel):
    """The final structured risk assessment suitable for review by a human analyst."""
    submission_id: str = Field(..., description="Must match the incoming submission_id.")
    dimension_risks: list[DimensionRisk] = Field(..., description="Risk ratings across predefined dimensions.")
    composite_score: float = Field(..., description="Derived numerical risk score (e.g., 1.0 to 5.0).")
    recommended_authorization_level: str = Field(
        ..., 
        description="Final recommendation: 'Approved', 'Conditional', or 'Rejected'."
    )
    follow_up_questions: list[str] = Field(
        ..., 
        description="Clarification questions where information is missing or inconsistent."
    )
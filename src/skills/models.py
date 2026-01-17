from __future__ import annotations


from pydantic import BaseModel, Field

from src.engine.types import WorkflowStage


class AnalyzeAndPlanSkillOutput(BaseModel):
    """Structured fields returned by the analyze and plan skill."""

    chain_of_thought: str = Field(
        default="",
        description="Detailed reasoning about the user's query and the context.",
    )
    next_stage: WorkflowStage = Field(
        default=WorkflowStage.COORDINATOR,
        description="Recommended next workflow stage.",
    )


class AnalyzeEmailSkillOutput(BaseModel):
    """Structured output from email analysis skill."""

    main_topic: str = Field(
        ...,
        description="Short label defining the email subject (e.g., 'Login Error', 'Quote Request')",
    )
    business_category: str = Field(
        ...,
        description="Department assignment (e.g., Sales, HR, Tech Support, Accounting)",
    )
    contact_data: str = Field(
        ...,
        description="Extracted email addresses or phone numbers from the body/signature",
    )
    urgency: str = Field(
        ...,
        description="Urgency level: Low, Medium, or High (based on keywords like 'ASAP', 'failure')",
    )
    sentiment: str = Field(
        ..., description="Emotional analysis: Positive, Neutral, or Negative"
    )
    summary: str = Field(
        ..., description="One-sentence abstract of the problem for management review"
    )

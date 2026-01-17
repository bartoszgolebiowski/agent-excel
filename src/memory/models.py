from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from src.tools.models import HelloWorldRequest
from src.engine.types import WorkflowStage


class UrgencyLevel(str, Enum):
    """Urgency classification for emails."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class SentimentLevel(str, Enum):
    """Sentiment classification for emails."""

    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class EmailAnalysisResult(BaseModel):
    """Structured data extracted from email analysis."""

    main_topic: str = Field(..., description="Short label defining the email subject")
    business_category: str = Field(
        ...,
        description="Department assignment (Sales, HR, Tech Support, Accounting, etc.)",
    )
    contact_data: str = Field(
        ..., description="Extracted email addresses or phone numbers"
    )
    urgency: UrgencyLevel = Field(
        ..., description="Urgency assessment (Low/Medium/High)"
    )
    sentiment: SentimentLevel = Field(
        ..., description="Emotional analysis (Positive/Neutral/Negative)"
    )
    summary: str = Field(..., description="One-sentence abstract of the problem")
    event_date: datetime = Field(
        default_factory=datetime.now, description="Date the message was received"
    )
    source_file: str = Field(..., description="Original email filename")


class EmailProcessingState(BaseModel):
    """Current state of email processing workflow."""

    inbox_files: List[str] = Field(
        default_factory=list, description="List of files found in inbox"
    )
    current_file_index: int = Field(
        default=0, description="Index of currently processing file"
    )
    current_file_content: Optional[str] = Field(
        default=None, description="Content of the currently loaded email"
    )
    current_analysis: Optional[EmailAnalysisResult] = Field(
        default=None, description="Analysis result of current email"
    )
    processed_count: int = Field(
        default=0, description="Number of emails processed in this cycle"
    )

    def has_more_files(self) -> bool:
        """Check if there are more files to process."""
        return self.current_file_index < len(self.inbox_files)

    def get_current_file(self) -> Optional[str]:
        """Get the current file path to process."""
        if self.has_more_files():
            return self.inbox_files[self.current_file_index]
        return None

    def advance_to_next_file(self) -> None:
        """Move to the next file in the queue."""
        self.current_file_index += 1
        self.current_file_content = None
        self.current_analysis = None


class ConstitutionalMemory(BaseModel):
    """The "agent's DNA." Security and ethical principles that the agent MUST NOT break. Guardrails."""


class WorkingMemory(BaseModel):
    """The context of the current session (RAM). What we're talking about "right now.\" """

    query_analysis: Optional[Any] = Field(
        default=None, description="Analysis and plan of the current query."
    )
    email_processing: EmailProcessingState = Field(
        default_factory=EmailProcessingState,
        description="Current email processing state",
    )


class WorkflowTransition(BaseModel):
    """Record of a workflow stage transition."""

    from_stage: WorkflowStage
    to_stage: WorkflowStage
    timestamp: datetime = Field(default_factory=datetime.now)
    reason: Optional[str] = None


class WorkflowMemory(BaseModel):
    """The State Machine. Where am I in the business process?"""

    current_stage: WorkflowStage = Field(
        default=WorkflowStage.INITIAL, description="Current stage in the workflow"
    )
    goal: str = Field(..., description="The initial goal that started the workflow.")
    history: List[WorkflowTransition] = Field(
        default_factory=list, description="Historical record of stage transitions."
    )

    def record_transition(
        self, to_stage: WorkflowStage, reason: Optional[str] = None
    ) -> None:
        """Helper to append a transition to history if the stage changed."""
        if self.current_stage != to_stage:
            self.history.append(
                WorkflowTransition(
                    from_stage=self.current_stage, to_stage=to_stage, reason=reason
                )
            )
            self.current_stage = to_stage


class EpisodicMemory(BaseModel):
    """What happened? Interaction history, event logs."""


class SemanticMemory(BaseModel):
    """What do I know? The knowledge base (RAG), facts about the world and the user."""


class ProceduralMemory(BaseModel):
    """How do I do it? Tool definitions, APIs, user manuals."""


class ResourceMemory(BaseModel):
    """Do I have the resources? System status, API availability, limits."""


class AgentState(BaseModel):
    """Full memory object available to the engine layer."""

    core: ConstitutionalMemory
    working: WorkingMemory
    workflow: WorkflowMemory
    episodic: EpisodicMemory
    semantic: SemanticMemory
    procedural: ProceduralMemory
    resource: ResourceMemory

    def get_hello_world_request(self) -> HelloWorldRequest:
        """Constructs a HelloWorldRequest from the agent state."""
        return HelloWorldRequest(query="Hello, World!")

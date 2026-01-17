from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, Optional

from pydantic import BaseModel

from datetime import datetime

from src.skills.base import SkillName
from src.skills.models import AnalyzeAndPlanSkillOutput, AnalyzeEmailSkillOutput
from src.tools.models import (
    HelloWorldResponse,
    ToolName,
    CheckInboxResponse,
    ReadEmailResponse,
    SaveToExcelResponse,
    ArchiveEmailResponse,
)

from .models import (
    AgentState,
    ConstitutionalMemory,
    EmailAnalysisResult,
    EpisodicMemory,
    ProceduralMemory,
    ResourceMemory,
    SemanticMemory,
    SentimentLevel,
    UrgencyLevel,
    WorkflowMemory,
    WorkingMemory,
)
from src.engine.types import WorkflowStage

SkillHandler = Callable[[AgentState, BaseModel], AgentState]
ToolHandler = Callable[[AgentState, BaseModel], AgentState]


def create_initial_state(
    goal: Optional[str] = None,
    core: Optional[ConstitutionalMemory] = None,
    semantic: Optional[SemanticMemory] = None,
    episodic: Optional[EpisodicMemory] = None,
    workflow: Optional[WorkflowMemory] = None,
    working: Optional[WorkingMemory] = None,
    procedural: Optional[ProceduralMemory] = None,
    resource: Optional[ResourceMemory] = None,
) -> AgentState:
    """Initialize a fully-populated state tree."""
    if goal is None and workflow is None:
        raise ValueError("Either goal or workflow must be provided")

    core = core or ConstitutionalMemory()
    semantic = semantic or SemanticMemory()
    episodic = episodic or EpisodicMemory()
    workflow = workflow or WorkflowMemory(goal=goal)  # type: ignore
    working = working or WorkingMemory()
    procedural = procedural or ProceduralMemory()
    resource = resource or ResourceMemory()

    return AgentState(
        core=core,
        semantic=semantic,
        episodic=episodic,
        workflow=workflow,
        working=working,
        procedural=procedural,
        resource=resource,
    )


def update_state_from_skill(
    state: AgentState, skill: SkillName, output: BaseModel
) -> AgentState:
    """Route a structured skill output to its handler."""

    handler = _SKILL_HANDLERS.get(skill)
    if handler is None:
        raise ValueError(f"No handler registered for skill {skill}")
    return handler(state, output)


def skill_analyze_and_plan_handler(
    state: AgentState, output: AnalyzeAndPlanSkillOutput
) -> AgentState:
    """Handler for analyze and plan skill that updates workflow with analysis and plan."""
    new_state = deepcopy(state)
    # Advance to the recommended stage and record transition
    new_state.workflow.record_transition(
        to_stage=output.next_stage, reason=output.chain_of_thought
    )
    return new_state


def skill_analyze_email_handler(
    state: AgentState, output: AnalyzeEmailSkillOutput
) -> AgentState:
    """Handler for email analysis skill that stores extracted data."""
    new_state = deepcopy(state)

    # Convert skill output to EmailAnalysisResult
    current_file = new_state.working.email_processing.get_current_file()
    if current_file is None:
        raise ValueError("No current file to analyze")

    analysis = EmailAnalysisResult(
        main_topic=output.main_topic,
        business_category=output.business_category,
        contact_data=output.contact_data,
        urgency=UrgencyLevel(output.urgency),
        sentiment=SentimentLevel(output.sentiment),
        summary=output.summary,
        event_date=datetime.now(),
        source_file=current_file,
    )

    new_state.working.email_processing.current_analysis = analysis
    new_state.workflow.record_transition(
        to_stage=WorkflowStage.SAVE_TO_EXCEL, reason="Email analysis completed"
    )

    return new_state


_SKILL_HANDLERS: Dict[SkillName, SkillHandler] = {
    SkillName.ANALYZE_AND_PLAN: skill_analyze_and_plan_handler,  # type: ignore
    SkillName.ANALYZE_EMAIL: skill_analyze_email_handler,  # type: ignore
}


def update_state_from_tool(
    state: AgentState, tool: ToolName, output: BaseModel
) -> AgentState:
    """Route a structured tool output to its handler."""

    handler = _TOOL_HANDLERS.get(tool)
    if handler is None:
        raise ValueError(f"No handler registered for tool {tool}")
    return handler(state, output)


def tool_welcome_handler(state: AgentState, output: HelloWorldResponse) -> AgentState:
    """Example tool handler that updates the episodic memory with a welcome message."""
    new_state = deepcopy(state)
    new_state.workflow.record_transition(
        to_stage=WorkflowStage.COORDINATOR, reason="Initial tool execution completed."
    )
    return new_state


def tool_check_inbox_handler(
    state: AgentState, output: CheckInboxResponse
) -> AgentState:
    """Handler for check inbox tool that stores list of files to process."""
    new_state = deepcopy(state)

    # If we're in CHECK_NEXT_EMAIL stage, we're checking for more files
    if state.workflow.current_stage == WorkflowStage.CHECK_NEXT_EMAIL:
        if new_state.working.email_processing.has_more_files():
            # There are more files to process
            new_state.workflow.record_transition(
                to_stage=WorkflowStage.ANALYZE_EMAIL,
                reason=f"Processing next email ({new_state.working.email_processing.current_file_index + 1}/{len(new_state.working.email_processing.inbox_files)})",
            )
        else:
            # All files processed
            new_state.workflow.record_transition(
                to_stage=WorkflowStage.COMPLETED,
                reason=f"All {new_state.working.email_processing.processed_count} emails processed",
            )
    else:
        # Initial inbox check
        new_state.working.email_processing.inbox_files = output.files
        new_state.working.email_processing.current_file_index = 0

        if output.count > 0:
            new_state.workflow.record_transition(
                to_stage=WorkflowStage.ANALYZE_EMAIL,
                reason=f"Found {output.count} email(s) to process",
            )
        else:
            new_state.workflow.record_transition(
                to_stage=WorkflowStage.COMPLETED, reason="No emails found in inbox"
            )

    return new_state


def tool_read_email_handler(state: AgentState, output: ReadEmailResponse) -> AgentState:
    """Handler for read email tool that stores email content."""
    new_state = deepcopy(state)
    new_state.working.email_processing.current_file_content = output.content
    new_state.workflow.record_transition(
        to_stage=WorkflowStage.ANALYZE_EMAIL, reason=f"Loaded email: {output.file_name}"
    )
    return new_state


def tool_save_to_excel_handler(
    state: AgentState, output: SaveToExcelResponse
) -> AgentState:
    """Handler for save to Excel tool."""
    new_state = deepcopy(state)
    new_state.workflow.record_transition(
        to_stage=WorkflowStage.ARCHIVE_EMAIL, reason="Analysis saved to Excel"
    )
    return new_state


def tool_archive_email_handler(
    state: AgentState, output: ArchiveEmailResponse
) -> AgentState:
    """Handler for archive email tool."""
    new_state = deepcopy(state)
    new_state.working.email_processing.processed_count += 1
    new_state.working.email_processing.advance_to_next_file()

    new_state.workflow.record_transition(
        to_stage=WorkflowStage.CHECK_NEXT_EMAIL, reason="Email archived successfully"
    )

    return new_state


_TOOL_HANDLERS: Dict[ToolName, ToolHandler] = {
    ToolName.HELLO_WORLD: tool_welcome_handler,  # type: ignore
    ToolName.CHECK_INBOX: tool_check_inbox_handler,  # type: ignore
    ToolName.READ_EMAIL: tool_read_email_handler,  # type: ignore
    ToolName.SAVE_TO_EXCEL: tool_save_to_excel_handler,  # type: ignore
    ToolName.ARCHIVE_EMAIL: tool_archive_email_handler,  # type: ignore
}

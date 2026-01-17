from __future__ import annotations

from typing import Dict, Tuple, Union

from .types import ActionType, WorkflowStage
from ..skills.base import SkillName
from ..tools.models import ToolName


TRANSITIONS: Dict[WorkflowStage, Tuple[ActionType, Union[SkillName, ToolName], str]] = {
    WorkflowStage.INITIAL: (
        ActionType.TOOL,
        ToolName.HELLO_WORLD,
        "Analyzing the user query and planning next steps",
    ),
    WorkflowStage.COORDINATOR: (
        ActionType.LLM_SKILL,
        SkillName.ANALYZE_AND_PLAN,
        "Coordinating the next actions based on the current state",
    ),
    WorkflowStage.COMPLETED: (
        ActionType.COMPLETE,
        SkillName.HELLO_WORLD,
        "Workflow completed successfully",
    ),
    # Email processing workflow stages
    WorkflowStage.CHECK_INBOX: (
        ActionType.TOOL,
        ToolName.CHECK_INBOX,
        "Checking inbox folder for new emails",
    ),
    WorkflowStage.ANALYZE_EMAIL: (
        ActionType.LLM_SKILL,
        SkillName.ANALYZE_EMAIL,
        "Analyzing email content and extracting structured data",
    ),
    WorkflowStage.SAVE_TO_EXCEL: (
        ActionType.TOOL,
        ToolName.SAVE_TO_EXCEL,
        "Saving email analysis to Excel report",
    ),
    WorkflowStage.ARCHIVE_EMAIL: (
        ActionType.TOOL,
        ToolName.ARCHIVE_EMAIL,
        "Moving processed email to archive folder",
    ),
    WorkflowStage.CHECK_NEXT_EMAIL: (
        ActionType.TOOL,
        ToolName.CHECK_INBOX,
        "Checking if there are more emails to process",
    ),
}

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from pydantic import BaseModel

from src.memory.models import AgentState
from src.tools.models import (
    ToolName,
    CheckInboxRequest,
    CheckInboxResponse,
    ReadEmailRequest,
    ReadEmailResponse,
    SaveToExcelRequest,
    SaveToExcelResponse,
    ArchiveEmailRequest,
    ArchiveEmailResponse,
)
from src.tools.email_tools import (
    check_inbox,
    read_email,
    save_to_excel,
    archive_email,
)
from src.tools.hello_world import HelloWorldClient


@dataclass(frozen=True, slots=True)
class ToolExecutor:
    """Executor responsible for dispatching tool calls."""

    inbox_path: str
    archive_path: str
    excel_path: str
    hello_world_client: HelloWorldClient

    @classmethod
    def from_env(cls) -> "ToolExecutor":
        """Create a tool executor from environment variables."""
        # Get paths from environment or use defaults
        inbox_path = os.getenv("INBOX_PATH", "data/inbox")
        archive_path = os.getenv("ARCHIVE_PATH", "data/archive")
        excel_path = os.getenv("EXCEL_PATH", "data/email_report.xlsx")

        return cls(
            inbox_path=inbox_path,
            archive_path=archive_path,
            excel_path=excel_path,
            hello_world_client=HelloWorldClient(),
        )

    def execute(self, tool_name: ToolName, state: AgentState) -> BaseModel:
        """Execute the specified tool with the current state."""
        if tool_name == ToolName.HELLO_WORLD:
            request = state.get_hello_world_request()
            return self.hello_world_client.call(request)

        elif tool_name == ToolName.CHECK_INBOX:
            # Determine if this is initial check or checking for next file
            if state.workflow.current_stage.value == "CHECK_NEXT_EMAIL":
                # Just check if there are more files in the current queue
                # The state manager will decide what to do
                return CheckInboxResponse(
                    files=state.working.email_processing.inbox_files,
                    count=len(state.working.email_processing.inbox_files),
                )
            else:
                # Initial check - scan the inbox directory
                request = CheckInboxRequest(inbox_path=self.inbox_path)
                return check_inbox(request)

        elif tool_name == ToolName.READ_EMAIL:
            current_file = state.working.email_processing.get_current_file()
            if not current_file:
                raise ValueError("No current file to read")
            request = ReadEmailRequest(file_path=current_file)
            return read_email(request)

        elif tool_name == ToolName.SAVE_TO_EXCEL:
            analysis = state.working.email_processing.current_analysis
            if not analysis:
                raise ValueError("No analysis available to save")

            request = SaveToExcelRequest(
                excel_path=self.excel_path,
                main_topic=analysis.main_topic,
                business_category=analysis.business_category,
                contact_data=analysis.contact_data,
                urgency=analysis.urgency.value,
                sentiment=analysis.sentiment.value,
                summary=analysis.summary,
                event_date=analysis.event_date.isoformat(),
                source_file=analysis.source_file,
            )
            return save_to_excel(request)

        elif tool_name == ToolName.ARCHIVE_EMAIL:
            current_file = state.working.email_processing.get_current_file()
            if not current_file:
                raise ValueError("No current file to archive")

            request = ArchiveEmailRequest(
                file_path=current_file,
                archive_path=self.archive_path,
            )
            return archive_email(request)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

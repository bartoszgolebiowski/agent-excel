from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel


class ToolName(str, Enum):
    """Names of available tools."""

    HELLO_WORLD = "hello_world"
    CHECK_INBOX = "check_inbox"
    READ_EMAIL = "read_email"
    SAVE_TO_EXCEL = "save_to_excel"
    ARCHIVE_EMAIL = "archive_email"


class HelloWorldRequest(BaseModel):
    """A simple request model for testing connectivity."""

    query: str


class HelloWorldResponse(BaseModel):
    """A simple response model for testing connectivity."""

    message: str


class CheckInboxRequest(BaseModel):
    """Request to check the inbox folder for new emails."""

    inbox_path: str


class CheckInboxResponse(BaseModel):
    """Response with list of files found in inbox."""

    files: List[str]
    count: int


class ReadEmailRequest(BaseModel):
    """Request to read an email file."""

    file_path: str


class ReadEmailResponse(BaseModel):
    """Response with email content."""

    content: str
    file_name: str


class SaveToExcelRequest(BaseModel):
    """Request to save email analysis to Excel."""

    excel_path: str
    main_topic: str
    business_category: str
    contact_data: str
    urgency: str
    sentiment: str
    summary: str
    event_date: str
    source_file: str


class SaveToExcelResponse(BaseModel):
    """Response confirming save to Excel."""

    success: bool
    message: str


class ArchiveEmailRequest(BaseModel):
    """Request to archive a processed email."""

    file_path: str
    archive_path: str


class ArchiveEmailResponse(BaseModel):
    """Response confirming email archival."""

    success: bool
    message: str

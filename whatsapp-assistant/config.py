"""
WhatsApp Assistant Configuration - Settings for WhatsApp bot, Google Drive, and AI.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WhatsAppConfig:
    """Configuration for the WhatsApp assistant."""

    # Twilio WhatsApp API
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # Backend API
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

    # Google Drive
    GOOGLE_DRIVE_CREDENTIALS: str = os.getenv(
        "GOOGLE_DRIVE_CREDENTIALS", "./credentials/google_drive_service.json"
    )
    GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # n8n Webhook
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")

    # Google Calendar
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    GOOGLE_CALENDAR_CREDENTIALS: str = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS", "./credentials/google_calendar_service.json"
    )

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30"))
    MAX_REQUESTS_PER_USER: int = int(os.getenv("MAX_REQUESTS_PER_USER", "10"))

    # Allowed users (phone numbers)
    ALLOWED_USERS: List[str] = field(default_factory=lambda: os.getenv(
        "ALLOWED_USERS", ""
    ).split(",") if os.getenv("ALLOWED_USERS") else [])

    # Command prefix
    COMMAND_PREFIX: str = "/"

    # Available commands
    COMMANDS = {
        "/case": "Search and track court cases",
        "/causelist": "Check today's cause list",
        "/drive": "Google Drive file operations",
        "/ai": "AI-powered case analysis",
        "/remind": "Set hearing reminders",
        "/status": "Check case status",
        "/help": "Show available commands",
    }

    def is_user_allowed(self, phone: str) -> bool:
        """Check if a phone number is in the allowed users list."""
        if not self.ALLOWED_USERS or self.ALLOWED_USERS == [""]:
            return True  # Allow all if no whitelist set
        return phone in self.ALLOWED_USERS

    def get_help_message(self) -> str:
        """Generate help message listing all commands."""
        lines = ["⚖️ *Court Automation Assistant*\n", "Available commands:\n"]
        for cmd, desc in self.COMMANDS.items():
            lines.append(f"  {cmd} - {desc}")
        lines.append("\nType any command to get started!")
        return "\n".join(lines)


@dataclass
class N8NConfig:
    """Configuration for n8n workflow integration."""

    BASE_URL: str = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    API_KEY: str = os.getenv("N8N_API_KEY", "")

    # Workflow webhook paths
    WEBHOOKS = {
        "drive_commands": "/webhook/drive-commands",
        "ai_summary": "/webhook/ai-summary",
        "calendar_sync": "/webhook/calendar-sync",
        "case_update": "/webhook/case-update",
    }

    def get_webhook_url(self, workflow: str) -> str:
        """Get full webhook URL for a workflow."""
        path = self.WEBHOOKS.get(workflow, "")
        return f"{self.BASE_URL}{path}"

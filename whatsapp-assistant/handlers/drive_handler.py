"""
Google Drive Handler - Manage Google Drive operations via WhatsApp commands.
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from google.oauth2 import service_account  # type: ignore[import-not-found]
    from googleapiclient.discovery import build  # type: ignore[import-not-found]
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from config import WhatsAppConfig  # type: ignore[import-not-found]


class DriveHandler:
    """Handle Google Drive operations triggered from WhatsApp messages."""

    def __init__(self):
        self.config = WhatsAppConfig()
        self.service = None
        if GOOGLE_AVAILABLE:
            self._init_drive_service()

    def _init_drive_service(self):
        """Initialize Google Drive API service."""
        try:
            creds_file = self.config.GOOGLE_DRIVE_CREDENTIALS
            if os.path.exists(creds_file):
                creds = service_account.Credentials.from_service_account_file(
                    creds_file,
                    scopes=["https://www.googleapis.com/auth/drive"],
                )
                self.service = build("drive", "v3", credentials=creds)
                logger.info("Google Drive service initialized")
        except Exception as e:
            logger.warning(f"Google Drive initialization failed: {e}")

    async def handle_command(self, command: str, args: List[str], user_phone: str) -> str:
        """Route drive commands to appropriate handlers."""
        if not self.service:
            return "⚠️ Google Drive is not configured. Please set up credentials."

        sub_command = args[0].lower() if args else "help"
        params: Optional[List[str]] = list(args[1:]) if len(args) > 1 else []  # type: ignore[call-overload]

        if sub_command == "list":
            return await self._list_files(params, user_phone)
        elif sub_command == "search":
            return await self._search_files(params, user_phone)
        elif sub_command == "upload":
            return await self._upload_info(params, user_phone)
        elif sub_command == "download":
            return await self._download_file(params, user_phone)
        elif sub_command == "share":
            return await self._share_file(params, user_phone)
        elif sub_command == "info":
            return await self._file_info(params, user_phone)
        elif sub_command == "recent":
            return await self._recent_files(params, user_phone)
        else:
            return await self._help(params, user_phone)

    async def _list_files(self, params: Optional[List[str]], user_phone: str) -> str:
        """List files in a folder or root."""
        folder_id = params[0] if params else self.config.GOOGLE_DRIVE_FOLDER_ID or "root"
        query = f"'{folder_id}' in parents and trashed = false"

        try:
            if self.service is None:
                return "⚠️ Google Drive is not configured."
            results = self.service.files().list(  # type: ignore[union-attr]
                q=query, pageSize=15,
                fields="files(id, name, mimeType, modifiedTime, size)",
                orderBy="modifiedTime desc",
            ).execute()
            files = results.get("files", [])

            if not files:
                return "📂 No files found in this folder."

            response = "📂 *Files in folder:*\n\n"
            for i, f in enumerate(files, 1):
                icon = self._get_file_icon(f.get("mimeType", ""))
                size = self._format_size(int(f.get("size", 0))) if f.get("size") else ""
                response += f"{i}. {icon} {f['name']}"
                if size:
                    response += f" ({size})"
                response += "\n"
            return response
        except Exception as e:
            return f"⚠️ Error listing files: {str(e)}"

    async def _search_files(self, params: Optional[List[str]], user_phone: str) -> str:
        """Search for files by name."""
        if not params:
            return "⚠️ Usage: /drive search <query>"

        query_text = " ".join(params)
        query = f"name contains '{query_text}' and trashed = false"

        try:
            if self.service is None:
                return "⚠️ Google Drive is not configured."
            results = self.service.files().list(  # type: ignore[union-attr]
                q=query, pageSize=10,
                fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            ).execute()
            files = results.get("files", [])

            if not files:
                return f"🔍 No files found matching: *{query_text}*"

            response = f"🔍 *Search results for '{query_text}':*\n\n"
            for i, f in enumerate(files, 1):
                response += f"{i}. 📄 {f['name']}\n"
                if f.get("webViewLink"):
                    response += f"   🔗 {f['webViewLink']}\n"
            return response
        except Exception as e:
            return f"⚠️ Search failed: {str(e)}"

    async def _download_file(self, params: Optional[List[str]], user_phone: str) -> str:
        """Get download link for a file."""
        if not params:
            return "⚠️ Usage: /drive download <filename>"

        filename = " ".join(params)
        query = f"name = '{filename}' and trashed = false"

        try:
            if self.service is None:
                return "⚠️ Google Drive is not configured."
            results = self.service.files().list(  # type: ignore[union-attr]
                q=query, pageSize=1,
                fields="files(id, name, webContentLink, webViewLink)",
            ).execute()
            files = results.get("files", [])

            if not files:
                return f"❌ File not found: {filename}"

            f = files[0]
            link = f.get("webContentLink") or f.get("webViewLink", "N/A")
            return f"📥 *Download link for {f['name']}:*\n\n🔗 {link}"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def _share_file(self, params: Optional[List[str]], user_phone: str) -> str:
        """Share a file with another user."""
        if not params or len(params) < 2:
            return "⚠️ Usage: /drive share <filename> <email>"

        filename, email = params[0], params[1]  # type: ignore[index]

        try:
            if self.service is None:
                return "⚠️ Google Drive is not configured."
            query = f"name = '{filename}' and trashed = false"
            results = self.service.files().list(  # type: ignore[union-attr]
                q=query, pageSize=1, fields="files(id, name)"
            ).execute()
            files = results.get("files", [])

            if not files:
                return f"❌ File not found: {filename}"

            permission = {"type": "user", "role": "reader", "emailAddress": email}
            self.service.permissions().create(  # type: ignore[union-attr]
                fileId=files[0]["id"], body=permission, sendNotificationEmail=True,
            ).execute()

            return f"✅ *{filename}* shared with {email}"
        except Exception as e:
            return f"⚠️ Sharing failed: {str(e)}"

    async def _file_info(self, params: Optional[List[str]], user_phone: str) -> str:
        """Get detailed info about a file."""
        if not params:
            return "⚠️ Usage: /drive info <filename>"

        filename = " ".join(params)
        query = f"name = '{filename}' and trashed = false"

        try:
            if self.service is None:
                return "⚠️ Google Drive is not configured."
            results = self.service.files().list(  # type: ignore[union-attr]
                q=query, pageSize=1,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime, owners, webViewLink)",
            ).execute()
            files = results.get("files", [])

            if not files:
                return f"❌ File not found: {filename}"

            f = files[0]
            size = self._format_size(int(f.get("size", 0))) if f.get("size") else "N/A"
            owner = f.get("owners", [{}])[0].get("displayName", "Unknown")

            return (
                f"ℹ️ *File Information:*\n\n"
                f"📄 *Name:* {f['name']}\n"
                f"📦 *Size:* {size}\n"
                f"📝 *Type:* {f.get('mimeType', 'Unknown')}\n"
                f"👤 *Owner:* {owner}\n"
                f"📅 *Modified:* {f.get('modifiedTime', 'Unknown')[:10]}\n"
                f"🔗 *Link:* {f.get('webViewLink', 'N/A')}"
            )
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def _recent_files(self, params: Optional[List[str]], user_phone: str) -> str:
        """List recently modified files."""
        try:
            if self.service is None:
                return "⚠️ Google Drive is not configured."
            results = self.service.files().list(  # type: ignore[union-attr]
                pageSize=10,
                fields="files(id, name, modifiedTime)",
                orderBy="modifiedTime desc",
                q="trashed = false",
            ).execute()
            files = results.get("files", [])

            if not files:
                return "📂 No recent files found."

            response = "🕐 *Recently Modified Files:*\n\n"
            for i, f in enumerate(files, 1):
                mod_time = f.get("modifiedTime", "")[:10]
                response += f"{i}. 📄 {f['name']} ({mod_time})\n"
            return response
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def _upload_info(self, params: Optional[List[str]], user_phone: str) -> str:
        """Show upload instructions."""
        return (
            "📤 *To upload a file:*\n\n"
            "1. Send the file/document via WhatsApp\n"
            "2. Add the caption: /drive upload <folder_name>\n\n"
            "The file will be uploaded to the specified folder."
        )

    async def _help(self, params: Optional[List[str]] = None, user_phone: str = "") -> str:
        """Show drive command help."""
        return (
            "📁 *Google Drive Commands:*\n\n"
            "• /drive list [folder_id] - List files\n"
            "• /drive search <query> - Search files\n"
            "• /drive download <name> - Get download link\n"
            "• /drive share <name> <email> - Share file\n"
            "• /drive info <name> - File details\n"
            "• /drive recent - Recently modified\n"
            "• /drive upload - Upload instructions\n"
        )

    @staticmethod
    def _get_file_icon(mime_type: str) -> str:
        """Get emoji icon based on MIME type."""
        if "folder" in mime_type:
            return "📁"
        elif "document" in mime_type or "word" in mime_type:
            return "📝"
        elif "spreadsheet" in mime_type or "excel" in mime_type:
            return "📊"
        elif "presentation" in mime_type:
            return "📽️"
        elif "pdf" in mime_type:
            return "📕"
        elif "image" in mime_type:
            return "🖼️"
        return "📄"

    @staticmethod
    def _format_size(size_bytes: float) -> str:
        """Format file size to human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

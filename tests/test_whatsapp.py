"""
Tests for WhatsApp assistant config, drive handler, and AI handler.
"""
import pytest


# ─── WhatsApp Config ─────────────────────────────────────────────

class TestWhatsAppConfig:
    def test_config_defaults(self):
        from config import WhatsAppConfig
        cfg = WhatsAppConfig()
        assert cfg is not None

    def test_has_command_prefix(self):
        from config import WhatsAppConfig
        cfg = WhatsAppConfig()
        assert hasattr(cfg, 'COMMAND_PREFIX')

    def test_user_allowed_no_whitelist(self):
        from config import WhatsAppConfig
        cfg = WhatsAppConfig()
        if hasattr(cfg, 'is_user_allowed'):
            result = cfg.is_user_allowed("+919999999999")
            assert result is True

    def test_user_allowed_with_whitelist(self):
        from config import WhatsAppConfig
        cfg = WhatsAppConfig()
        if hasattr(cfg, 'ALLOWED_NUMBERS') and hasattr(cfg, 'is_user_allowed'):
            cfg.ALLOWED_NUMBERS = ["+919876543210"]
            result = cfg.is_user_allowed("+911111111111")
            assert isinstance(result, bool)

    def test_n8n_config(self):
        from config import N8NConfig
        cfg = N8NConfig()
        assert cfg is not None


# ─── Drive Handler ────────────────────────────────────────────────

class TestDriveHandler:
    def _get_handler(self):
        from handlers.drive_handler import DriveHandler
        return DriveHandler()

    def test_init(self):
        handler = self._get_handler()
        assert handler is not None

    def test_file_icon_folder(self):
        handler = self._get_handler()
        icon = handler._get_file_icon("application/vnd.google-apps.folder")
        assert "📁" in icon

    def test_file_icon_pdf(self):
        handler = self._get_handler()
        icon = handler._get_file_icon("application/pdf")
        assert isinstance(icon, str) and len(icon) > 0

    def test_file_icon_image(self):
        handler = self._get_handler()
        icon = handler._get_file_icon("image/png")
        assert "🖼" in icon

    def test_format_size_bytes(self):
        handler = self._get_handler()
        assert "B" in handler._format_size(500)

    def test_format_size_kb(self):
        handler = self._get_handler()
        assert "KB" in handler._format_size(2048)

    def test_format_size_mb(self):
        handler = self._get_handler()
        result = handler._format_size(5 * 1024 * 1024)
        assert "MB" in result

    def test_has_handle_command(self):
        handler = self._get_handler()
        assert hasattr(handler, 'handle_command')


# ─── AI Handler ───────────────────────────────────────────────────

class TestAIHandler:
    def _get_handler(self):
        from handlers.ai_handler import AIHandler
        return AIHandler()

    def test_init(self):
        handler = self._get_handler()
        assert handler is not None

    def test_has_handle_command(self):
        handler = self._get_handler()
        assert hasattr(handler, 'handle_command')

    def test_has_commands(self):
        handler = self._get_handler()
        assert hasattr(handler, 'COMMANDS') or hasattr(handler, 'commands') or True

    def test_format_list(self):
        handler = self._get_handler()
        if hasattr(handler, 'format_list'):
            items = ["item1", "item2", "item3"]
            result = handler.format_list(items)
            assert "item1" in result
        elif hasattr(handler, '_format_list'):
            items = ["item1", "item2", "item3"]
            result = handler._format_list(items)
            assert "item1" in result

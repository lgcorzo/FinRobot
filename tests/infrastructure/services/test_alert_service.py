"""Tests for AlertsService."""

from unittest.mock import patch

from finrobot.infrastructure.services.alert_service import AlertsService


class TestAlertsService:
    """Test suite for AlertsService."""

    def test_alerts_service_instantiation(self):
        """Test that AlertsService can be instantiated with defaults."""
        service = AlertsService()
        assert service.enable is True
        assert service.app_name == "finrobot"
        assert service.timeout is None

    def test_alerts_service_disabled(self):
        """Test AlertsService when disabled."""
        service = AlertsService(enable=False)
        assert service.enable is False

    def test_alerts_service_custom_app_name(self):
        """Test AlertsService with custom app name."""
        service = AlertsService(app_name="custom_app")
        assert service.app_name == "custom_app"

    @patch("finrobot.infrastructure.services.alert_service.notification")
    def test_notify_sends_notification(self, mock_notification):
        """Test that notify() calls plyer notification."""
        service = AlertsService()
        service.notify(title="Test Title", message="Test Message")

        mock_notification.notify.assert_called_once_with(
            title="Test Title",
            message="Test Message",
            app_name="finrobot",
            timeout=None,
        )

    @patch("finrobot.infrastructure.services.alert_service.notification")
    def test_notify_disabled_prints_instead(self, mock_notification, capsys):
        """Test that notify() prints when disabled."""
        service = AlertsService(enable=False)
        service.notify(title="Test Title", message="Test Message")

        mock_notification.notify.assert_not_called()
        captured = capsys.readouterr()
        assert "Test Title" in captured.out
        assert "Test Message" in captured.out

    @patch("finrobot.infrastructure.services.alert_service.notification")
    def test_notify_handles_exception(self, mock_notification, capsys):
        """Test that notify() handles plyer exceptions gracefully."""
        mock_notification.notify.side_effect = Exception("No notification implementation")

        service = AlertsService()
        service.notify(title="Test Title", message="Test Message")

        captured = capsys.readouterr()
        assert "Notification ignored" in captured.out

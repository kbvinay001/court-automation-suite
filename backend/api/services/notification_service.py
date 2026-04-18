"""
Notification Service - Multi-channel notifications for case updates and alerts.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime, date
import logging
import httpx

logger = logging.getLogger(__name__)

# Email config
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)

# WhatsApp / Twilio config
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER", "")


class NotificationService:
    """Send notifications via email, WhatsApp, and SMS."""

    # ─────────────────── EMAIL ───────────────────

    async def send_email(
        self, to_email: str, subject: str, body_html: str, body_text: Optional[str] = None
    ) -> bool:
        """Send an email notification."""
        if not SMTP_USER:
            logger.warning("SMTP not configured, skipping email")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = FROM_EMAIL
            msg["To"] = to_email
            msg["Subject"] = subject

            if body_text:
                msg.attach(MIMEText(body_text, "plain"))
            msg.attach(MIMEText(body_html, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Email failed to {to_email}: {e}")
            return False

    # ─────────────────── WHATSAPP ───────────────────

    async def send_whatsapp(self, to_phone: str, message: str) -> bool:  # type: ignore[return-value]
        """Send a WhatsApp message via Twilio."""
        if not TWILIO_SID:
            logger.warning("Twilio not configured, skipping WhatsApp")
            return False

        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data={
                        "From": f"whatsapp:{TWILIO_WHATSAPP}",
                        "To": f"whatsapp:{to_phone}",
                        "Body": message,
                    },
                    auth=(TWILIO_SID, TWILIO_TOKEN),
                )
                if response.status_code == 201:
                    logger.info(f"WhatsApp sent to {to_phone}")
                    return True
                else:
                    logger.error(f"WhatsApp failed: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return False

    # ─────────────────── CASE NOTIFICATIONS ───────────────────

    async def notify_case_listed(self, case_data: Dict, recipients: List[Dict]):
        """Notify when a tracked case appears in a cause list."""
        case_number = case_data.get("case_number", "")
        court_name = case_data.get("court_name", "")
        listing_date = case_data.get("listing_date", "")

        subject = f"📋 Case {case_number} Listed - {court_name}"
        email_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1a365d; color: white; padding: 20px; text-align: center;">
                <h2>⚖️ Case Listed in Cause List</h2>
            </div>
            <div style="padding: 20px; background: #f7fafc;">
                <p><strong>Case Number:</strong> {case_number}</p>
                <p><strong>Court:</strong> {court_name}</p>
                <p><strong>Listing Date:</strong> {listing_date}</p>
                <p><strong>Petitioner:</strong> {case_data.get('petitioner', 'N/A')}</p>
                <p><strong>Respondent:</strong> {case_data.get('respondent', 'N/A')}</p>
                {f'<p><strong>Court No:</strong> {case_data.get("court_number", "")}</p>' if case_data.get("court_number") else ''}
                {f'<p><strong>Bench:</strong> {case_data.get("bench", "")}</p>' if case_data.get("bench") else ''}
            </div>
            <div style="padding: 10px; text-align: center; color: #718096; font-size: 12px;">
                Court Automation Suite
            </div>
        </div>
        """

        whatsapp_msg = (
            f"📋 *Case Listed*\n\n"
            f"*Case:* {case_number}\n"
            f"*Court:* {court_name}\n"
            f"*Date:* {listing_date}\n"
            f"*Parties:* {case_data.get('petitioner', '')} vs {case_data.get('respondent', '')}"
        )

        for recipient in recipients:
            if recipient.get("notify_email"):
                await self.send_email(recipient["notify_email"], subject, email_body)
            if recipient.get("notify_phone"):
                await self.send_whatsapp(recipient["notify_phone"], whatsapp_msg)

    async def notify_hearing_reminder(self, case_data: Dict, recipients: List[Dict]):
        """Send hearing reminder notification."""
        case_number = case_data.get("case_number", "")
        hearing_date = case_data.get("next_hearing_date", "")
        court_name = case_data.get("court_name", "")

        subject = f"⏰ Hearing Reminder: {case_number} on {hearing_date}"
        email_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #c53030; color: white; padding: 20px; text-align: center;">
                <h2>⏰ Upcoming Hearing Reminder</h2>
            </div>
            <div style="padding: 20px; background: #fff5f5;">
                <p><strong>Case Number:</strong> {case_number}</p>
                <p><strong>Hearing Date:</strong> {hearing_date}</p>
                <p><strong>Court:</strong> {court_name}</p>
                <p><strong>Petitioner:</strong> {case_data.get('petitioner', 'N/A')}</p>
                <p><strong>Respondent:</strong> {case_data.get('respondent', 'N/A')}</p>
            </div>
            <div style="padding: 10px; text-align: center; color: #718096; font-size: 12px;">
                Court Automation Suite
            </div>
        </div>
        """

        whatsapp_msg = (
            f"⏰ *Hearing Reminder*\n\n"
            f"*Case:* {case_number}\n"
            f"*Date:* {hearing_date}\n"
            f"*Court:* {court_name}\n"
            f"Please prepare accordingly."
        )

        for recipient in recipients:
            if recipient.get("notify_email"):
                await self.send_email(recipient["notify_email"], subject, email_body)
            if recipient.get("notify_phone"):
                await self.send_whatsapp(recipient["notify_phone"], whatsapp_msg)

    async def send_daily_digest(self, user_data: Dict, digest: Dict):
        """Send daily digest of tracked case updates."""
        email = user_data.get("email", "")
        if not email:
            return

        cases_count = len(digest.get("cases", []))
        subject = f"📊 Daily Court Digest - {cases_count} updates ({date.today().strftime('%d %b')})"

        cases_html = ""
        for case in digest.get("cases", []):
            cases_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{case.get('case_number', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{case.get('court_name', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{case.get('status', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{case.get('next_hearing_date', 'N/A')}</td>
            </tr>
            """

        email_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #2d3748; color: white; padding: 20px; text-align: center;">
                <h2>📊 Daily Court Digest</h2>
                <p>{date.today().strftime('%d %B %Y')}</p>
            </div>
            <div style="padding: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #edf2f7;">
                        <th style="padding: 8px; text-align: left;">Case</th>
                        <th style="padding: 8px; text-align: left;">Court</th>
                        <th style="padding: 8px; text-align: left;">Status</th>
                        <th style="padding: 8px; text-align: left;">Next Hearing</th>
                    </tr>
                    {cases_html}
                </table>
            </div>
        </div>
        """

        await self.send_email(email, subject, email_body)

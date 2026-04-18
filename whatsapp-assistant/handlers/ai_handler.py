"""
AI Handler - AI-powered case analysis and queries via WhatsApp.
"""

import logging
from typing import List, Optional

import httpx  # type: ignore[import-not-found]

from config import WhatsAppConfig  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


class AIHandler:
    """Handle AI-powered queries from WhatsApp messages."""

    def __init__(self):
        self.config = WhatsAppConfig()
        self.api_base = self.config.API_BASE_URL

    async def handle_command(self, command: str, args: List[str], user_phone: str) -> str:
        """Route AI commands to appropriate handlers."""
        sub_command = args[0].lower() if args else "help"
        params: Optional[List[str]] = list(args[1:]) if len(args) > 1 else []  # type: ignore[call-overload]

        if sub_command == "summary":
            return await self._summarize_case(params, user_phone)
        elif sub_command == "predict":
            return await self._predict_outcome(params, user_phone)
        elif sub_command == "analyze":
            return await self._analyze_cases(params, user_phone)
        elif sub_command == "brief":
            return await self._generate_brief(params, user_phone)
        elif sub_command == "extract":
            return await self._extract_entities(params, user_phone)
        elif sub_command == "ask":
            return await self._ask_question(params, user_phone)
        else:
            return await self._help(params, user_phone)

    async def _summarize_case(self, params: Optional[List[str]], user_phone: str) -> str:  # type: ignore[return-value]
        """Get AI summary of a case."""
        if not params:
            return "⚠️ Usage: /ai summary <case_number>"

        case_number = params[0]

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                # Get case details
                response = await client.get(
                    f"{self.api_base}/scraper/case/{case_number}"
                )

                if response.status_code != 200:
                    return f"❌ Case not found: {case_number}"

                case_data = response.json().get("data", {})

                # Call AI service for summary
                summary = await self._call_ai(
                    "Summarize this Indian court case concisely for a WhatsApp message. "
                    "Include key parties, current status, and important dates.",
                    str(case_data),
                )

                if summary:
                    return (
                        f"🤖 *AI Case Summary*\n"
                        f"📋 *Case:* {case_number}\n\n"
                        f"{summary}"
                    )
                return f"⚠️ AI summary unavailable for {case_number}"
        except Exception as e:
            logger.error(f"AI summary failed: {e}")
            return f"⚠️ Error: {str(e)}"

    async def _predict_outcome(self, params: Optional[List[str]], user_phone: str) -> str:  # type: ignore[return-value]
        """Predict case outcome using AI."""
        if not params:
            return "⚠️ Usage: /ai predict <case_number>"

        case_number = params[0]

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(
                    f"{self.api_base}/analytics/predictions",
                    params={"case_number": case_number},
                )

                if response.status_code != 200:
                    return f"❌ Prediction unavailable for {case_number}"

                prediction = response.json().get("prediction", {})

                return (
                    f"🔮 *AI Case Prediction*\n"
                    f"📋 *Case:* {case_number}\n\n"
                    f"📊 *Likely Outcome:* {prediction.get('likely_outcome', 'N/A')}\n"
                    f"🎯 *Confidence:* {prediction.get('confidence', 'N/A')}\n"
                    f"⏰ *Timeline:* {prediction.get('estimated_timeline', 'N/A')}\n"
                    f"\n💡 *Key Factors:*\n"
                    f"{self._format_list(prediction.get('key_factors', []))}\n"
                    f"\n📝 *Recommendations:*\n"
                    f"{self._format_list(prediction.get('recommendations', []))}"
                )
        except Exception as e:
            logger.error(f"AI prediction failed: {e}")
            return f"⚠️ Error: {str(e)}"

    async def _analyze_cases(self, params: Optional[List[str]], user_phone: str) -> str:  # type: ignore[return-value]
        """Analyze trends across user's tracked cases."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(
                    f"{self.api_base}/analytics/dashboard",
                    params={"user_id": user_phone},
                )

                if response.status_code != 200:
                    return "❌ Analytics unavailable"

                data = response.json().get("data", {})

                return (
                    f"📊 *Your Case Analytics*\n\n"
                    f"📈 *Total Cases:* {data.get('total_cases', 0)}\n"
                    f"⏳ *Pending:* {data.get('pending_cases', 0)}\n"
                    f"✅ *Disposed:* {data.get('disposed_cases', 0)}\n"
                    f"📅 *Upcoming Hearings:* {data.get('upcoming_hearings', 0)}\n"
                    f"📊 *Active Rate:* {data.get('active_rate', 0)}%"
                )
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def _generate_brief(self, params: Optional[List[str]], user_phone: str) -> str:
        """Generate a legal brief template."""
        if not params:
            return "⚠️ Usage: /ai brief <case_number> [type]\n\nTypes: reply, petition, application"

        case_number = params[0]
        brief_type = params[1] if len(params) > 1 else "reply"

        try:
            result = await self._call_ai(
                f"Generate a concise {brief_type} brief outline for Indian court case {case_number}. "
                f"Keep it brief enough for WhatsApp. Use bullet points.",
                f"Case: {case_number}, Brief type: {brief_type}",
            )

            if result:
                return f"📝 *{brief_type.title()} Brief Template*\n📋 *Case:* {case_number}\n\n{result}"
            return "⚠️ Brief generation unavailable"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def _extract_entities(self, params: Optional[List[str]], user_phone: str) -> str:
        """Extract legal entities from text."""
        if not params:
            return "⚠️ Usage: /ai extract <text containing legal references>"

        text = " ".join(params)

        try:
            result = await self._call_ai(
                "Extract legal entities (case numbers, names, dates, statutes, courts) "
                "from this text. Format as a WhatsApp-friendly list.",
                text,
            )

            if result:
                return f"🔍 *Extracted Legal Entities:*\n\n{result}"
            return "⚠️ Entity extraction unavailable"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def _ask_question(self, params: Optional[List[str]], user_phone: str) -> str:
        """Ask a general legal question to AI."""
        if not params:
            return "⚠️ Usage: /ai ask <your legal question>"

        question = " ".join(params)

        try:
            result = await self._call_ai(
                "You are a legal assistant specializing in Indian law. "
                "Answer concisely for WhatsApp. Include relevant statutes and precedents "
                "when applicable. Add a disclaimer that this is AI-generated guidance.",
                question,
            )

            if result:
                return f"🤖 *AI Legal Assistant*\n\n{result}"
            return "⚠️ AI assistant unavailable"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    async def _call_ai(self, system_prompt: str, user_message: str) -> Optional[str]:
        """Make an AI API call."""
        if not self.config.OPENAI_API_KEY:
            return None

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.config.OPENAI_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000,
                    },
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"AI call failed: {e}")
        return None

    async def _help(self, params: Optional[List[str]] = None, user_phone: str = "") -> str:
        """Show AI command help."""
        return (
            "🤖 *AI Commands:*\n\n"
            "• /ai summary <case_no> - Case summary\n"
            "• /ai predict <case_no> - Outcome prediction\n"
            "• /ai analyze - Your case analytics\n"
            "• /ai brief <case_no> [type] - Brief template\n"
            "• /ai extract <text> - Extract legal entities\n"
            "• /ai ask <question> - Legal Q&A\n"
        )

    @staticmethod
    def _format_list(items) -> str:
        """Format a list for WhatsApp display."""
        if isinstance(items, list):
            return "\n".join(f"  • {item}" for item in items[:5])  # type: ignore[call-overload]
        return str(items) if items else "N/A"

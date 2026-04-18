"""
AI Service - Generative AI and ML integration for case analysis and predictions.
"""

import os
from typing import Dict, Optional, List
from datetime import datetime
import logging

import httpx

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")


class AIService:
    """AI-powered analysis and predictions for court cases."""

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL
        self.base_url = OPENAI_BASE_URL

    async def _call_openai(self, messages: List[Dict], temperature: float = 0.3) -> Optional[str]:
        """Make an API call to OpenAI."""
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": 2000,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return None

    async def summarize_case(self, case_data: Dict) -> Optional[str]:
        """Generate an AI summary of a court case."""
        case_info = (
            f"Case Number: {case_data.get('case_number', 'N/A')}\n"
            f"Court: {case_data.get('court_name', 'N/A')}\n"
            f"Type: {case_data.get('case_type', 'N/A')}\n"
            f"Status: {case_data.get('status', 'N/A')}\n"
            f"Petitioner: {case_data.get('petitioner', 'N/A')}\n"
            f"Respondent: {case_data.get('respondent', 'N/A')}\n"
            f"Subject: {case_data.get('subject', 'N/A')}\n"
            f"Act/Section: {case_data.get('act', 'N/A')} {case_data.get('section', '')}\n"
            f"Filing Date: {case_data.get('filing_date', 'N/A')}\n"
            f"Next Hearing: {case_data.get('next_hearing_date', 'N/A')}\n"
        )

        hearings = case_data.get("hearings", [])
        if hearings:
            case_info += "\nHearing History:\n"
            for h in hearings[-10:]:  # Last 10 hearings
                case_info += (
                    f"  - {h.get('date', '')}: {h.get('order_summary', 'No order details')}\n"
                )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a legal research assistant specializing in Indian courts. "
                    "Provide concise, professional case summaries suitable for advocates. "
                    "Highlight key issues, current stage, and critical observations."
                ),
            },
            {
                "role": "user",
                "content": f"Please provide a comprehensive summary of this case:\n\n{case_info}",
            },
        ]

        return await self._call_openai(messages)

    async def predict_outcome(self, case_data: Dict) -> Dict:
        """Predict likely outcome and next steps for a case."""
        case_info = (
            f"Case: {case_data.get('case_number', '')}\n"
            f"Type: {case_data.get('case_type', '')}\n"
            f"Court: {case_data.get('court_name', '')}\n"
            f"Subject: {case_data.get('subject', '')}\n"
            f"Status: {case_data.get('status', '')}\n"
            f"Hearings count: {len(case_data.get('hearings', []))}\n"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a legal analyst. Based on case patterns in Indian courts, "
                    "provide structured predictions in JSON format with keys: "
                    "'likely_outcome', 'confidence' (low/medium/high), "
                    "'estimated_timeline', 'key_factors', 'recommendations'."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze and predict the outcome for:\n\n{case_info}",
            },
        ]

        result = await self._call_openai(messages, temperature=0.2)
        if result:
            try:
                import json
                return json.loads(result)
            except (json.JSONDecodeError, ValueError):
                return {
                    "likely_outcome": "Analysis pending",
                    "confidence": "low",
                    "raw_analysis": result,
                }
        return {"error": "AI analysis unavailable"}

    async def analyze_patterns(self, cases: List[Dict]) -> Optional[str]:
        """Analyze patterns across multiple cases."""
        summary = f"Analyzing {len(cases)} cases:\n\n"
        for case in cases[:20]:  # type: ignore[index]  # Limit to 20 cases
            summary += (
                f"- {case.get('case_number', '')}: {case.get('case_type', '')} "
                f"at {case.get('court_name', '')} - {case.get('status', '')}\n"
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a legal data analyst. Identify patterns, trends, and "
                    "notable observations across the provided Indian court cases. "
                    "Focus on case type distribution, court workload, disposal patterns, "
                    "and adjournment trends."
                ),
            },
            {"role": "user", "content": summary},
        ]

        return await self._call_openai(messages, temperature=0.4)

    async def generate_legal_brief(self, case_data: Dict, brief_type: str = "reply") -> Optional[str]:
        """Generate a legal brief template for a case."""
        case_info = (
            f"Case: {case_data.get('case_number', '')}\n"
            f"Court: {case_data.get('court_name', '')}\n"
            f"Type: {case_data.get('case_type', '')}\n"
            f"Subject: {case_data.get('subject', '')}\n"
            f"Petitioner: {case_data.get('petitioner', '')}\n"
            f"Respondent: {case_data.get('respondent', '')}\n"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a legal drafting assistant for Indian courts. "
                    f"Generate a professional {brief_type} brief template. "
                    "Include proper court formatting, legal citations placeholders, "
                    "and structured arguments. Mark areas needing human input with [___]."
                ),
            },
            {
                "role": "user",
                "content": f"Generate a {brief_type} brief template for:\n\n{case_info}",
            },
        ]

        return await self._call_openai(messages, temperature=0.5)

    async def extract_entities(self, text: str) -> Dict:
        """Extract legal entities from text (names, dates, case numbers, statutes)."""
        messages = [
            {
                "role": "system",
                "content": (
                    "Extract legal entities from the text. Return JSON with keys: "
                    "'case_numbers', 'names', 'dates', 'statutes', 'courts', 'sections'. "
                    "Each value should be a list of extracted entities."
                ),
            },
            {"role": "user", "content": f"Extract entities from:\n\n{text}"},
        ]

        result = await self._call_openai(messages, temperature=0.1)
        if result:
            try:
                import json
                return json.loads(result)
            except (json.JSONDecodeError, ValueError):
                return {"raw": result}
        return {}

    async def get_court_insights(self, court_name: str) -> Dict:
        """Get AI-generated insights for a court."""
        from utils.database import aggregate

        # Get court stats
        pipeline = [
            {"$match": {"court_name": court_name} if court_name != "All Courts" else {}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                }
            },
        ]
        stats = await aggregate("cases", pipeline)
        stats_text = "\n".join([f"  {s['_id']}: {s['count']}" for s in stats])

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a court analytics expert. Provide insights and "
                    "recommendations based on court statistics. Be concise."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Provide insights for {court_name}:\n\n"
                    f"Case distribution by status:\n{stats_text}"
                ),
            },
        ]

        result = await self._call_openai(messages, temperature=0.4)
        return {"court": court_name, "insights": result or "Insights unavailable"}

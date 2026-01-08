"""Azure OpenAI client wrapper for deterministic investor reasoning."""

import os
from typing import Dict, Any

from openai import AzureOpenAI, OpenAIError

from backend.reasoning import prompts


class AzureReasoningClient:
    """Thin wrapper around Azure OpenAI for deterministic reasoning."""

    def __init__(self) -> None:
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self._client = None

        if self.is_configured:
            self._client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
            )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.endpoint and self.deployment)

    def generate_reasoning(self, snapshot: Dict[str, Any]) -> Dict[str, str]:
        """Generate investor reasoning. Falls back to deterministic template if unconfigured."""
        if not self.is_configured:
            return self._fallback_reasoning(snapshot)

        user_prompt = prompts.REASONING_USER_TEMPLATE.format(**snapshot)
        try:
            response = self._client.chat.completions.create(
                model=self.deployment,
                temperature=0.1,
                max_tokens=320,
                messages=[
                    {"role": "system", "content": prompts.REASONING_SYSTEM_PROMPT.strip()},
                    {"role": "user", "content": user_prompt.strip()},
                ],
            )
            content = response.choices[0].message.content if response.choices else ""
            parsed = self._parse_response(content)
            if parsed:
                return parsed
        except OpenAIError:
            pass  # Fall back to deterministic reasoning

        return self._fallback_reasoning(snapshot)

    def _parse_response(self, content: str) -> Dict[str, str]:
        import json

        if not content:
            return {}
        try:
            return json.loads(content)
        except Exception:
            return {}

    def _fallback_reasoning(self, snapshot: Dict[str, Any]) -> Dict[str, str]:
        """Deterministic, template-based reasoning for offline/demo use."""
        severity = str(snapshot.get("severity", "")).upper()
        top_driver = "execution risk"
        drivers = snapshot.get("risk_drivers", []) or []
        if drivers:
            top_driver = drivers[0].get("label", top_driver)

        risk_score = snapshot.get("risk_score", 0)
        trend = snapshot.get("trend", "stable")
        name = snapshot.get("name", "The company")

        # Simple deterministic text blocks
        why = (
            f"{top_driver} is the dominant signal for {name}. "
            f"Current risk score is {risk_score:.1f} ({severity})."
        )
        next_steps = (
            "If unaddressed, expect the current trajectory to persist over the next 2-3 weeks. "
            f"Trend is {trend}; monitor for further escalation."
        )
        if severity == "HIGH":
            action = "Schedule partner-led intervention within 7 days; secure execution and runway clarity."
        elif severity == "MEDIUM":
            action = "Increase monitoring cadence to weekly and request updated execution and runway plans."
        else:
            action = "Maintain standard monitoring; prepare contingency if trend reverses."

        return {
            "why_this_matters": why,
            "what_typically_happens_next": next_steps,
            "recommended_investor_action": action,
        }

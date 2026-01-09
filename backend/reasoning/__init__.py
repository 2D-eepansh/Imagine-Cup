"""Reasoning layer for investor-grade explanations (Phase 2).

Separation of concerns:
- Azure ML models detect and score risk.
- Azure OpenAI generates investor-ready reasoning and guidance.

This package provides:
- Prompt templates tailored for IC/VC consumption
- Azure OpenAI client wrapper
- Deterministic orchestration with caching to avoid repeat calls
"""

from reasoning.orchestrator import get_investor_reasoning

__all__ = ["get_investor_reasoning"]

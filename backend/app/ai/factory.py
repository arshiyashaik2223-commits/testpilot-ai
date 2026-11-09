
import os

from app.ai.providers.base import AIProvider


def get_ai_provider() -> AIProvider:
    """
    Selects the AI provider using AI_PROVIDER from the environment.
    Supported providers: Claude and Groq.
    """
    provider_name = os.environ.get("AI_PROVIDER", "groq").lower()

    if provider_name == "groq":
        from app.ai.providers.groq_provider import GroqProvider
        return GroqProvider()

    if provider_name == "claude":
        from app.ai.providers.claude_provider import ClaudeProvider
        return ClaudeProvider()

    raise ValueError(
        f"Unknown AI_PROVIDER '{provider_name}'. "
        "Supported: groq, claude."
    )

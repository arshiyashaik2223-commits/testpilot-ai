import os

from app.ai.providers.base import AIProvider


def get_ai_provider() -> AIProvider:
    """
    Reads AI_PROVIDER from the environment and returns the matching provider.
    To add OpenAI or Gemini later: write a class implementing AIProvider
    (see app/ai/providers/base.py), then add one branch here. Nothing that
    calls get_ai_provider() needs to change.
    """
    provider_name = os.environ.get("AI_PROVIDER", "claude").lower()

    if provider_name == "claude":
        from app.ai.providers.claude_provider import ClaudeProvider
        return ClaudeProvider()

    raise ValueError(
        f"Unknown AI_PROVIDER '{provider_name}'. Supported: claude "
        f"(openai/gemini not implemented yet)."
    )

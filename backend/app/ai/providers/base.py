from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Every AI provider (Claude, OpenAI, Gemini) implements this same interface.
    The rest of the app only ever talks to this interface, never to a specific
    provider's SDK directly — that's what makes the provider swappable.
    """

    @abstractmethod
    def generate_test_cases(self, requirement_text: str) -> list[dict]:
        """
        Takes a plain-English requirement and returns a list of test case
        dicts, each shaped like:
        {
            "scenario": str,
            "test_type": "positive" | "negative" | "boundary" | "security" | "validation",
            "preconditions": str,
            "steps": list[str],
            "test_data": str,
            "expected_result": str,
            "priority": "Low" | "Medium" | "High" | "Critical",
        }
        """
        raise NotImplementedError

    @abstractmethod
    def generate_test_code(self, test_case: dict) -> str:
        """
        Takes a test case dict (same shape as returned by generate_test_cases)
        and returns a single Pytest test function as a plain Python source string.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_failure(self, scenario: str, expected_result: str, code: str, output: str) -> dict:
        """
        Returns a dict shaped like:
        {
            "explanation": str,
            "likely_cause": str,
            "confidence": int,       # 0-100
            "category": str,         # one of FAILURE_CATEGORIES
            "severity": str,         # Low | Medium | High | Critical
            "suggested_fix": str,
        }
        """
        raise NotImplementedError

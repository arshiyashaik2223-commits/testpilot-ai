
import json
import os
import re

from groq import Groq

from app.ai.providers.base import AIProvider
from app.ai.prompts import (
    TEST_CASE_SYSTEM_PROMPT,
    build_test_case_user_prompt,
    TEST_CODE_SYSTEM_PROMPT,
    build_test_code_user_prompt,
    FAILURE_ANALYSIS_SYSTEM_PROMPT,
    build_failure_analysis_user_prompt,
)
from app.execution.security import find_forbidden_pattern
from app.models.failure_analysis import FAILURE_CATEGORIES, SEVERITY_LEVELS

VALID_TEST_TYPES = {"positive", "negative", "boundary", "security", "validation"}
VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}


class GroqProvider(AIProvider):

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )

        self.client = Groq(api_key=api_key)
        self.model = os.environ.get(
            "AI_MODEL", "openai/gpt-oss-120b"
        )

    def _generate(self, system_prompt, user_prompt, max_tokens):
        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Groq returned an empty response.")

        return content

    def generate_test_cases(self, requirement_text: str) -> list[dict]:
        if not requirement_text or not requirement_text.strip():
            raise ValueError("requirement_text must not be empty.")

        raw_text = self._generate(
            TEST_CASE_SYSTEM_PROMPT,
            build_test_case_user_prompt(requirement_text),
            4000,
        )

        return self._parse_and_validate(raw_text)

    def generate_test_code(self, test_case: dict) -> str:
        raw_code = self._generate(
            TEST_CODE_SYSTEM_PROMPT,
            build_test_code_user_prompt(test_case),
            2000,
        )

        cleaned = re.sub(
            r"^```(?:python)?|```$",
            "",
            raw_code.strip(),
            flags=re.MULTILINE,
        ).strip()

        forbidden = find_forbidden_pattern(cleaned)

        if forbidden:
            raise ValueError(
                f"AI-generated code contained a disallowed pattern "
                f"('{forbidden}') and was rejected."
            )

        return cleaned

    def analyze_failure(
        self,
        scenario: str,
        expected_result: str,
        code: str,
        output: str,
    ) -> dict:

        raw_text = self._generate(
            FAILURE_ANALYSIS_SYSTEM_PROMPT,
            build_failure_analysis_user_prompt(
                scenario, expected_result, code, output
            ),
            2500,
        )

        return self._parse_and_validate_analysis(raw_text)

    @staticmethod
    def _parse_and_validate_analysis(raw_text: str) -> dict:
        cleaned = re.sub(
            r"^```(?:json)?|```$",
            "",
            raw_text.strip(),
            flags=re.MULTILINE,
        ).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"AI response was not valid JSON: {exc}"
            ) from exc

        if not isinstance(parsed, dict):
            raise ValueError("AI response must be a single JSON object.")

        required_fields = [
            "explanation",
            "likely_cause",
            "confidence",
            "category",
            "severity",
            "suggested_fix",
        ]

        missing = [f for f in required_fields if f not in parsed]

        if missing:
            raise ValueError(
                f"AI response is missing fields: {missing}"
            )

        try:
            confidence = int(parsed["confidence"])
        except (TypeError, ValueError):
            confidence = 50

        parsed["confidence"] = max(0, min(100, confidence))

        if parsed["category"] not in FAILURE_CATEGORIES:
            parsed["category"] = "BUG"

        if parsed["severity"] not in SEVERITY_LEVELS:
            parsed["severity"] = "Medium"

        return parsed

    @staticmethod
    def _parse_and_validate(raw_text: str) -> list[dict]:
        cleaned = re.sub(
            r"^```(?:json)?|```$",
            "",
            raw_text.strip(),
            flags=re.MULTILINE,
        ).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"AI response was not valid JSON: {exc}"
            ) from exc

        if not isinstance(parsed, list) or not parsed:
            raise ValueError(
                "AI response must be a non-empty JSON array of test cases."
            )

        validated = []

        for i, item in enumerate(parsed):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Test case #{i} is not a JSON object."
                )

            required_fields = [
                "scenario",
                "test_type",
                "preconditions",
                "steps",
                "test_data",
                "expected_result",
                "priority",
            ]

            missing = [f for f in required_fields if f not in item]

            if missing:
                raise ValueError(
                    f"Test case #{i} is missing fields: {missing}"
                )

            if item["test_type"] not in VALID_TEST_TYPES:
                item["test_type"] = "positive"

            if item["priority"] not in VALID_PRIORITIES:
                item["priority"] = "Medium"

            if not isinstance(item["steps"], list):
                item["steps"] = [str(item["steps"])]

            validated.append(item)

        return validated

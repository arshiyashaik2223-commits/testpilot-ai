# Defense in depth: even though the code-generation prompt forbids these,
# an LLM can still produce them, and a user can hand-edit code after
# generation. This check runs both when code is saved and again right
# before execution, regardless of which AI provider produced it.
FORBIDDEN_CODE_PATTERNS = [
    "os.system", "subprocess", "eval(", "exec(", "compile(",
    "__import__", "socket", "shutil", "ctypes", "importlib",
    "open(",  # any file access — this MVP's tests should only call the API over HTTP
]


def find_forbidden_pattern(code: str) -> str | None:
    for pattern in FORBIDDEN_CODE_PATTERNS:
        if pattern in code:
            return pattern
    return None

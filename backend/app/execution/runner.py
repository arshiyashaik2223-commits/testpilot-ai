import os
import subprocess
import sys
import tempfile
import time

from app.execution.security import find_forbidden_pattern

EXECUTION_TIMEOUT_SECONDS = 30
MAX_OUTPUT_CHARS = 10000

# Resource limits are POSIX-only (Linux/Mac). On Windows this safety layer is
# skipped — timeout is still enforced by subprocess itself either way.
try:
    import resource
    HAS_RESOURCE_MODULE = True
except ImportError:
    HAS_RESOURCE_MODULE = False


def _limit_resources():
    """Runs in the child process, before the test code executes."""
    if not HAS_RESOURCE_MODULE:
        return
    cpu_seconds = EXECUTION_TIMEOUT_SECONDS
    memory_bytes = 256 * 1024 * 1024  # 256 MB
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))


def run_pytest_code(code: str, api_base_url: str | None = None) -> dict:
    """
    Writes `code` to a temp file and runs it with pytest in a subprocess.
    Returns {"status": "passed"|"failed"|"error", "output": str, "duration_ms": int}
    Never raises — execution problems become an "error" status with the reason in output.
    """
    forbidden = find_forbidden_pattern(code)
    if forbidden:
        return {
            "status": "error",
            "output": f"Execution blocked: code contains disallowed pattern '{forbidden}'.",
            "duration_ms": 0,
        }

    start = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="testpilot_run_") as tmp_dir:
        test_file_path = os.path.join(tmp_dir, "test_generated.py")
        with open(test_file_path, "w") as f:
            f.write(code)

        # Minimal environment — the sandboxed test only needs to know the
        # API base URL and have a usable Python path. It does not inherit
        # our real environment (no DB credentials, no secrets, etc).
        restricted_env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "API_BASE_URL": api_base_url or "http://localhost:8000",
            "PYTHONDONTWRITEBYTECODE": "1",
        }

        popen_kwargs = dict(
            cwd=tmp_dir,
            env=restricted_env,
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT_SECONDS,
        )
        if HAS_RESOURCE_MODULE:
            popen_kwargs["preexec_fn"] = _limit_resources

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file_path, "-v", "--tb=short"],
                **popen_kwargs,
            )
            duration_ms = int((time.perf_counter() - start) * 1000)
            combined_output = (result.stdout or "") + (result.stderr or "")
            combined_output = combined_output[:MAX_OUTPUT_CHARS]

            if result.returncode == 0:
                status = "passed"
            elif result.returncode == 1:
                status = "failed"  # pytest: tests ran, at least one assertion failed
            else:
                status = "error"  # pytest: collection error, internal error, etc.

            return {"status": status, "output": combined_output, "duration_ms": duration_ms}

        except subprocess.TimeoutExpired:
            duration_ms = int((time.perf_counter() - start) * 1000)
            return {
                "status": "error",
                "output": f"Execution timed out after {EXECUTION_TIMEOUT_SECONDS} seconds.",
                "duration_ms": duration_ms,
            }
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            return {
                "status": "error",
                "output": f"Execution failed to start: {exc}",
                "duration_ms": duration_ms,
            }

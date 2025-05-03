import concurrent.futures, logging
from typing import Dict

from lib.gemini_client import GeminiClient
from lib.openai_client import OpenAIClient

_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=2)

GEMINI_TIMEOUT = 55   # seconds
OPENAI_TIMEOUT  = 60  # seconds


class AIClient:
    """Try Gemini first; fall back to OpenAI. Hard‑time‑out each step."""

    def __init__(self) -> None:
        self._gemini = GeminiClient(model="gemini-2.5-flash-preview-04-17")
        self._openai = OpenAIClient(model="o4-mini")

    # ---- internal helpers -------------------------------------------------

    def _run_with_timeout(self, fn, timeout: int):
        """Run ``fn`` in the pool, enforcing *timeout* seconds."""
        fut = _POOL.submit(fn)
        try:
            return fut.result(timeout=timeout)
        finally:
            # if the work is still running, stop it so the thread is freed
            fut.cancel()

    # ---- public API -------------------------------------------------------

    def generate_conclusion(
        self,
        teacher_code_dict: Dict[str, str],
        student_code_dict: Dict[str, str],
    ) -> str:

        # ---------- 1) Gemini ------------------------------------------------
        gemini_error = None
        try:
            text = self._run_with_timeout(
                lambda: self._gemini.generate_conclusion(
                    teacher_code_dict, student_code_dict
                ),
                GEMINI_TIMEOUT,
            )
            return text, "Gemini (gemini-2.5-flash-preview)"
        except Exception as exc:
            gemini_error = exc          # keep it alive for later
            logging.warning(
                "Gemini failed or timed out after %ss → falling back to OpenAI: %s",
                GEMINI_TIMEOUT,
                exc,
            )

        # ---------- 2) OpenAI -----------------------------------------------
        try:
            text = self._run_with_timeout(
                lambda: self._openai.generate_conclusion(
                    teacher_code_dict, student_code_dict
                ),
                OPENAI_TIMEOUT,
            )
            return text, "OpenAI (o4-mini)"
        except Exception as openai_error:
            # raise a single RuntimeError that records both failures
            raise RuntimeError(
                f"Gemini error: {gemini_error!r} │ OpenAI error: {openai_error!r}"
            ) from openai_error

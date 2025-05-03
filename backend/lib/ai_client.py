import concurrent.futures, logging

from lib.gemini_client import GeminiClient
from lib.openai_client import OpenAIClient
from typing import Dict

_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=2)

GEMINI_TIMEOUT = 20
OPENAI_TIMEOUT = 30

class AIClient:
    """
    Try Gemini → fall back to OpenAI automatically.
    """

    def __init__(self):
        self._gemini = GeminiClient(model="gemini-2.5-flash-preview-04-17")
        self._openai = OpenAIClient(model="o4-mini")

    def _gemini_call(self, t: Dict[str, str], s: Dict[str, str]) -> str:
        return self._gemini.generate_conclusion(t, s)

    def _openai_call(self, t: Dict[str, str], s: Dict[str, str]) -> str:
        return self._openai.generate_conclusion(t, s)

    def generate_conclusion(self, teacher_code_dict, student_code_dict) -> str:
        # 1) Gemini (hard‑stop after 20 s)
        g_future = _POOL.submit(
            self._gemini_call, teacher_code_dict, student_code_dict
        )
        try:
            return g_future.result(timeout=GEMINI_TIMEOUT)
        except Exception as g_err:
            logging.warning(
                "Gemini failed or timed‑out (%s) – trying OpenAI (o4‑mini)", g_err
            )

        # 2) OpenAI (hard‑stop after 30 s)
        o_future = _POOL.submit(
            self._openai_call, teacher_code_dict, student_code_dict
        )
        try:
            return o_future.result(timeout=OPENAI_TIMEOUT)
        except Exception as o_err:
            return f"Gemini error: {g_err} │ OpenAI error: {o_err}"

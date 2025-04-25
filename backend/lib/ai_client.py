import logging

from lib.gemini_client import GeminiClient
from lib.openai_client import OpenAIClient


class AIClient:
    """
    Try Gemini → fall back to OpenAI automatically.
    """

    def __init__(self):
        self._gemini = GeminiClient(model="gemini-2.5-flash-preview-04-17")
        self._openai = OpenAIClient(model="o4-mini")

    # ------------------------------------------------------------------ #
    def generate_conclusion(self, teacher_code_dict, student_code_dict):
        try:
            return self._gemini.generate_conclusion(
                teacher_code_dict, student_code_dict
            )

        except Exception as g_err:
            logging.warning(
                "Gemini failed (%s). Falling back to OpenAI o4-mini.", g_err
            )

            try:
                return self._openai.generate_conclusion(
                    teacher_code_dict, student_code_dict
                )
            except Exception as o_err:
                raise RuntimeError(
                    f"Gemini error: {g_err} │ OpenAI error: {o_err}"
                ) from o_err

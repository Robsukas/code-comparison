import os
import google.generativeai as genai

from lib.prompt_builder import build_prompt


class GeminiClient:
    def __init__(self, model: str | None = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY env var is required")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model
        )

    def generate_conclusion(self, teacher_code_dict, student_code_dict):
        prompt = build_prompt(teacher_code_dict, student_code_dict)
        resp   = self.model.generate_content(prompt)
        return resp.text

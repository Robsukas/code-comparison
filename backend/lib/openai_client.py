import os
from typing import Dict

from openai import OpenAI
from lib.prompt_builder import build_prompt


class OpenAIClient:
    def __init__(self, model: str):
        if not model:
            raise ValueError("model must be supplied to OpenAIClient()")

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model  = model

    # ------------------------------------------------------------------ #
    def generate_conclusion(self,
                            teacher_code_dict: Dict[str, str],
                            student_code_dict: Dict[str, str]) -> str:
        prompt = build_prompt(teacher_code_dict, student_code_dict)

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert programming instructor analyzing code for functional equivalence. Focus on critical differences that affect the code's behavior.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Error generating conclusion: {e}"

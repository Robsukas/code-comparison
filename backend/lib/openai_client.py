"""
OpenAI Client Module

This module provides a client for interacting with OpenAI's API to generate
code analysis conclusions. It handles API configuration, model initialization,
and content generation for comparing teacher and student code.

Dependencies:
    - openai: Official OpenAI Python SDK
    - lib.prompt_builder: For constructing analysis prompts

Environment Variables:
    OPENAI_API_KEY: Required API key for OpenAI authentication
"""

import os
from typing import Dict

from openai import OpenAI
from lib.prompt_builder import build_prompt


class OpenAIClient:
    """
    Client for interacting with OpenAI's API to generate code analysis.
    
    This class handles the initialization and configuration of the OpenAI model,
    and provides methods for generating AI-powered code analysis conclusions.
    It uses a system prompt that positions the AI as an expert programming
    instructor focused on functional equivalence analysis.
    
    Attributes:
        client (OpenAI): Configured OpenAI client instance
        model (str): Name of the OpenAI model to use
    """

    def __init__(self, model: str):
        """
        Initialize the OpenAI client with API configuration and model setup.
        
        Args:
            model (str): The specific OpenAI model to use (e.g., 'gpt-4', 'gpt-3.5-turbo')
            
        Raises:
            ValueError: If model parameter is not provided
        """
        if not model:
            raise ValueError("model must be supplied to OpenAIClient()")

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model  = model

    def generate_conclusion(self,
                            teacher_code_dict: Dict[str, str],
                            student_code_dict: Dict[str, str]) -> str:
        """
        Generate an AI analysis conclusion comparing teacher and student code.
        
        This method uses OpenAI's chat completion API to analyze the code differences
        and generate a conclusion. It uses a system prompt that positions the AI as
        an expert programming instructor focused on functional equivalence.
        
        Args:
            teacher_code_dict (Dict[str, str]): Dictionary mapping filenames to teacher's code
            student_code_dict (Dict[str, str]): Dictionary mapping filenames to student's code
            
        Returns:
            str: The generated analysis conclusion, or an error message if generation fails
            
        Note:
            The system prompt instructs the AI to focus on critical differences
            that affect the code's behavior, emphasizing functional equivalence.
        """
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

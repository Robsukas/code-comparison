"""
Gemini AI Client Module

This module provides a client for interacting with Google's Gemini AI model.
It handles API configuration, model initialization, and content generation
for code analysis purposes.

Dependencies:
    - google.generativeai: Official Google Generative AI SDK
    - lib.prompt_builder: For constructing analysis prompts

Environment Variables:
    GEMINI_API_KEY: Required API key for Gemini authentication
"""

import os
import google.generativeai as genai

from lib.prompt_builder import build_prompt


class GeminiClient:
    """
    Client for interacting with Google's Gemini AI model.
    
    This class handles the initialization and configuration of the Gemini model,
    and provides methods for generating AI-powered code analysis conclusions.
    
    Attributes:
        model: Configured Gemini GenerativeModel instance
    """

    def __init__(self, model: str | None = None):
        """
        Initialize the Gemini client with API configuration and model setup.
        
        Args:
            model (str | None): The specific Gemini model to use. If None, uses default.
            
        Raises:
            ValueError: If GEMINI_API_KEY environment variable is not set
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY env var is required")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model
        )

    def generate_conclusion(self, teacher_code_dict, student_code_dict):
        """
        Generate an AI analysis conclusion comparing teacher and student code.
        
        Args:
            teacher_code_dict: Dictionary containing the teacher's code samples
            student_code_dict: Dictionary containing the student's code samples
            
        Returns:
            str: The generated analysis conclusion text
            
        Note:
            Uses the prompt_builder module to construct the analysis prompt
            before sending it to the Gemini model.
        """
        prompt = build_prompt(teacher_code_dict, student_code_dict)
        resp   = self.model.generate_content(prompt)
        return resp.text

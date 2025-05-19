"""
AI Client Module for Code Analysis

This module provides an AI-powered code analysis with a fallback mechanism, attempting to use
Gemini first and falling back to OpenAI if Gemini fails or times out. It implements
timeout protection for both services to ensure reliable operation.

Dependencies:
    - concurrent.futures: For thread pool execution and timeout management
    - lib.gemini_client: GeminiClient for primary AI analysis
    - lib.openai_client: OpenAIClient for fallback AI analysis

Constants:
    GEMINI_TIMEOUT (int): Maximum time in seconds to wait for Gemini response (55s)
    OPENAI_TIMEOUT (int): Maximum time in seconds to wait for OpenAI response (60s)
"""

import concurrent.futures, logging
from typing import Dict

from lib.gemini_client import GeminiClient
from lib.openai_client import OpenAIClient

# Thread pool for concurrent execution of AI requests
_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Timeout configurations for AI services
GEMINI_TIMEOUT = 55   # seconds
OPENAI_TIMEOUT = 60   # seconds


class AIClient:
    """
    AI Client that implements a fallback mechanism for code analysis.
    
    This class attempts to use Gemini first for code analysis, and if that fails
    or times out, it falls back to using OpenAI. Each attempt is protected by
    a hard timeout to ensure the system remains responsive.
    
    Attributes:
        _gemini (GeminiClient): Client for Gemini AI service
        _openai (OpenAIClient): Client for OpenAI service
    """

    def __init__(self) -> None:
        """
        Initialize the AI Client with both Gemini and OpenAI clients.
        
        Uses specific model versions:
        - Gemini: gemini-2.5-flash-preview-04-17
        - OpenAI: o4-mini
        """
        self._gemini = GeminiClient(model="gemini-2.5-flash-preview-04-17")
        self._openai = OpenAIClient(model="o4-mini")

    def _run_with_timeout(self, fn, timeout: int):
        """
        Execute a function with a timeout in the thread pool.
        
        Args:
            fn: The function to execute
            timeout (int): Maximum time in seconds to wait for the function to complete
            
        Returns:
            The result of the function execution
            
        Raises:
            TimeoutError: If the function execution exceeds the timeout
            Exception: Any exception raised by the function
        """
        # Submit the function to the thread pool for concurrent execution
        fut = _POOL.submit(fn)
        try:
            # Wait for the result with timeout protection
            return fut.result(timeout=timeout)
        finally:
            # Always cancel the future to prevent resource leaks
            fut.cancel()

    def generate_conclusion(
        self,
        teacher_code_dict: Dict[str, str],
        student_code_dict: Dict[str, str],
    ) -> str:
        """
        Generate a conclusion by comparing teacher and student code.
        
        Attempts to use Gemini first, falling back to OpenAI if Gemini fails.
        Each attempt is protected by a timeout to ensure system responsiveness.
        
        Args:
            teacher_code_dict (Dict[str, str]): Dictionary containing teacher's code
            student_code_dict (Dict[str, str]): Dictionary containing student's code
            
        Returns:
            str: The generated conclusion text
            
        Raises:
            RuntimeError: If both Gemini and OpenAI fail to generate a conclusion
        """
        gemini_error = None
        try:
            # First attempt: Try Gemini with timeout protection
            text = self._run_with_timeout(
                lambda: self._gemini.generate_conclusion(
                    teacher_code_dict, student_code_dict
                ),
                GEMINI_TIMEOUT,
            )
            return text, "Gemini (gemini-2.5-flash-preview)"
        except Exception as exc:
            # Store Gemini error for final error reporting if both attempts fail
            gemini_error = exc
            logging.warning(
                "Gemini failed or timed out after %ss → falling back to OpenAI: %s",
                GEMINI_TIMEOUT,
                exc,
            )

        try:
            # Second attempt: Try OpenAI with timeout protection
            text = self._run_with_timeout(
                lambda: self._openai.generate_conclusion(
                    teacher_code_dict, student_code_dict
                ),
                OPENAI_TIMEOUT,
            )
            return text, "OpenAI (o4-mini)"
        except Exception as openai_error:
            # If both attempts fail, raise a combined error with details from both services
            raise RuntimeError(
                f"Gemini error: {gemini_error!r} │ OpenAI error: {openai_error!r}"
            ) from openai_error

def build_prompt(teacher_code_dict: dict[str, str],
                 student_code_dict: dict[str, str]) -> str:
    """
    Returns the long, format-locked prompt string used by *all* LLM providers.
    """
    teacher_code = "\n\n".join(f"# File: {fn}\n{code}"
                               for fn, code in teacher_code_dict.items())
    student_code = "\n\n".join(f"# File: {fn}\n{code}"
                               for fn, code in student_code_dict.items())
    
    prompt = f"""
        Analyze the student code implementation for functional equivalence with the teacher code. The teacher code shows the expected behavior, while the student code is to be evaluated.

        TEACHER CODE:
        {teacher_code}

        STUDENT CODE:
        {student_code}

        Provide your analysis in the following exact format:

        FUNCTION ANALYSIS:
        #[filename1]/[function_name1]
        Status: [OK/ISSUES]
        [Recommendations/Issues]: [For OK status, list any recommendations or observations. For ISSUES status, list critical breaking issues.]

        #[filename1]/[function_name2]
        Status: [OK/ISSUES]
        [Recommendations/Issues]: [For OK status, list any recommendations or observations. For ISSUES status, list critical breaking issues.]

        #[filename2]/[function_name1]
        Status: [OK/ISSUES]
        [Recommendations/Issues]: [For OK status, list any recommendations or observations. For ISSUES status, list critical breaking issues.]
        ...

        FINAL CONCLUSION:
        [One paragraph summarizing the overall state of the code and any critical breaking issues that need attention]

        Guidelines:
        1. Use Status: OK if the function works correctly and any differences are non-breaking
        2. Use Status: ISSUES only for critical breaking issues that would cause the code to fail or produce incorrect results
        3. For Status: OK functions:
            - Use "Recommendations:" instead of "Issues:"
            - Write recommendations in clear, simple language that a student can easily understand
            - Focus on practical improvements rather than technical details
            - Keep each recommendation short and to the point
            - Avoid technical jargon unless necessary

        4. For Status: ISSUES functions:
           - Use "Issues:" to list critical breaking issues
           - Explain problems in simple terms
           - Be specific about what causes different behavior
        5. Keep the final conclusion brief and focused on critical breaking issues
        6. In the final conclusion, emphasize any functions with Status: ISSUES
        7. DO NOT analyze or comment on the teacher code
        8. ONLY provide feedback on the student code
        9. For code that doesn't have specific functions (like scripts with just main execution), use "main" as the function name

        Example format:
        FUNCTION ANALYSIS:
        #utils.py/encrypt
        Status: OK
        Recommendations: 
          - Consider using a dictionary for character mapping to improve performance
          - Add error handling for invalid characters

        #utils.py/decrypt
        Status: ISSUES
        Issues: 
          - The function crashes when given an empty string
          - The shift parameter is not properly validated

        #script.py/main
        Status: OK
        Recommendations:
          - Add input validation for edge cases
          - Consider adding logging for debugging purposes

        FINAL CONCLUSION:
        The implementation has critical issues in the decrypt function where it crashes on empty input and lacks proper parameter validation. The encrypt function works as expected, with some non-critical implementation differences. Script.py could use some extra logging.
        """

    return prompt
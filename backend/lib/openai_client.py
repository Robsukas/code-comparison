import os
from openai import OpenAI
from typing import Dict, Any

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate_conclusion(self, teacher_code: str, student_code: str, comparison_results: Dict[str, Any]) -> str:
        prompt = self._construct_prompt(teacher_code, student_code)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano", # gpt-4.1-nano, o3-mini, o4-mini, o1
                messages=[
                    {"role": "system", "content": "You are an expert programming instructor analyzing code for functional equivalence. Focus on critical differences that affect the code's behavior."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating conclusion: {str(e)}"

    def _construct_prompt(self, teacher_code: str, student_code: str) -> str:
        """Construct a focused prompt for the OpenAI API."""
        
        prompt = f"""Analyze the student code implementation for functional equivalence with the teacher code. The teacher code shows the expected behavior, while the student code is to be evaluated.

TEACHER CODE:
{teacher_code}

STUDENT CODE:
{student_code}

Provide your analysis in the following exact format:

FUNCTION ANALYSIS:
fn([function_name_1]):
Status: [OK/ISSUES]
[Recommendations/Issues]: [For OK status, list any recommendations or observations. For ISSUES status, list critical breaking issues.]

fn([function_name_2]):
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

Example format:
FUNCTION ANALYSIS:
fn(list_of_phones):
Status: OK
Recommendations: 
  - Consider using a dictionary instead of a list for faster phone lookups
  - Add checks for invalid phone numbers to make the code more robust

fn(phone_brands):
Status: ISSUES
Issues: 
  - The code crashes when given an empty list
  - When the same brand appears multiple times, it's counted incorrectly
...

FINAL CONCLUSION:
The implementation has critical issues in the phone_brands function where it crashes on empty input and returns incorrect results. Other functions work as expected, with some non-critical implementation differences."""

        return prompt 
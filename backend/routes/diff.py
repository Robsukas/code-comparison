"""
Code Comparison API Endpoint

This module provides the API endpoint for comparing student code against teacher code.
It handles:
- Code retrieval from GitLab
- Code type validation
- Structural and semantic comparison
- AI-powered code analysis (optional)

The endpoint supports both function-based and block-based code structures,
and can optionally use LLM (Language Learning Model) for generating
conclusions about the code differences.

Dependencies:
    - flask: For API routing and request handling
    - lib.strict_comparison: For detailed code comparison
    - lib.utils: For code analysis utilities
    - lib.gitlab_client: For code retrieval from GitLab
    - lib.ai_client: For AI-powered code analysis
"""

from flask import Blueprint, request, jsonify, current_app
from lib.strict_comparison import StrictComparator
from lib.utils import Utils
from lib.gitlab_client import GitLabClient
from lib.openai_client import OpenAIClient
from lib.ai_client import AIClient


diff_bp = Blueprint('diff', __name__)
gitlab_client = GitLabClient()
ai_client = AIClient()

@diff_bp.route('/api/diff', methods=['POST'])
def diff_endpoint():
    """
    Compare student code against teacher code and optionally generate AI analysis.
    
    This endpoint:
    1. Retrieves code from GitLab for both student and teacher
    2. Validates code types match
    3. Performs structural and semantic comparison
    4. Optionally generates AI analysis of differences
    
    Request JSON Parameters:
        student_id (str): Student's identifier
        exercise (str): Exercise identifier
        year (str): Academic year
        use_llm (bool, optional): Whether to use AI analysis. Defaults to True.
    
    Returns:
        JSON response with:
            - message: Status message
            - differences: Detailed code differences
            - conclusion: AI analysis (if use_llm=True)
            - llm_model: Model used for analysis
            - diff_error: Any comparison errors
            - llm_error: Any AI analysis errors
    
    Error Responses:
        400: Missing required parameters or code type mismatch
        500: GitLab retrieval failures
    """
    data = request.get_json()

    # Extract and validate required parameters
    student_id = data.get('student_id')
    exercise = data.get('exercise')
    year = data.get('year')
    use_llm = data.get('use_llm', True)

    if not all([student_id, exercise, year]):
        return jsonify({'error': 'student_id, exercise, and year are required.'}), 400

    # Fetch code from GitLab
    student_code_dict = gitlab_client.get_student_code(student_id, exercise, year)
    teacher_code_dict = gitlab_client.get_teacher_code(exercise, year)

    if not student_code_dict:
        return jsonify({
            'error': 'Failed to fetch code from GitLab',
            'details': 'Could not retrieve student code'
        }), 500
    
    if not teacher_code_dict:
        return jsonify({
            'error': 'Failed to fetch code from GitLab',
            'details': 'Could not retrieve teacher code'
        }), 500

    # Validate code types match between student and teacher code
    student_code = next(iter(student_code_dict.values()))
    teacher_code = next(iter(teacher_code_dict.values()))
    
    student_code_type = Utils.detect_code_type(student_code)
    teacher_code_type = Utils.detect_code_type(teacher_code)
    
    if student_code_type != teacher_code_type:
        return jsonify({
            'error': 'Code type mismatch',
            'details': f'Student code is {student_code_type} while teacher code is {teacher_code_type}'
        }), 400
    
    # Initialize result variables
    diff_error = None
    llm_error  = None
    differences = None
    conclusion  = None 
    llm_model  = None

    # Perform code comparison
    try:
        differences = Utils.compare_files(student_code_dict, teacher_code_dict)
    except Exception as e:
        diff_error = f"diff failed: {e}"
        current_app.logger.exception(diff_error)

    # Generate AI analysis if requested
    if use_llm:
        try:
            conclusion, llm_model = ai_client.generate_conclusion(teacher_code_dict, student_code_dict)
        except Exception as e:
            llm_error = f"LLM failed: {e}"
            current_app.logger.warning(llm_error)

    # Return comparison results
    return jsonify(
        message      = "ok",
        differences  = differences,
        conclusion   = conclusion,
        llm_model = llm_model,
        diff_error   = diff_error,
        llm_error    = llm_error,
    ), 200
from flask import Blueprint, request, jsonify
from lib.strict_comparison import StrictComparator
from lib.utils import Utils
from lib.gitlab_client import GitLabClient
from lib.openai_client import OpenAIClient
import code_diff as cd
import textwrap

diff_bp = Blueprint('diff', __name__)
gitlab_client = GitLabClient()
openai_client = OpenAIClient()

@diff_bp.route('/api/diff', methods=['POST'])
def diff_endpoint():
    data = request.get_json()

    student_id = data.get('student_id')
    exercise = data.get('exercise')
    year = data.get('year')
    use_llm = data.get('use_llm', True)

    if not all([student_id, exercise, year]):
        return jsonify({'error': 'student_id, exercise, and year are required.'}), 400

    # Fetch code from GitLab
    student_code = gitlab_client.get_student_code(student_id, exercise, year)
    teacher_code = gitlab_client.get_teacher_code(exercise, year)

    if not student_code:
        return jsonify({
            'error': 'Failed to fetch code from GitLab',
            'details': 'Could not retrieve student code'
        }), 500
    
    if not teacher_code:
        return jsonify({
            'error': 'Failed to fetch code from GitLab',
            'details': 'Could not retrieve teacher code'
        }), 500

    student_code = textwrap.dedent(student_code).strip()
    teacher_code = textwrap.dedent(teacher_code).strip()
    
    # Detect code type for both student and teacher code
    student_code_type = Utils.detect_code_type(student_code)
    teacher_code_type = Utils.detect_code_type(teacher_code)
    
    # If code types don't match, return an error
    if student_code_type != teacher_code_type:
        return jsonify({
            'error': 'Code type mismatch',
            'details': f'Student code is {student_code_type} while teacher code is {teacher_code_type}'
        }), 400
    
    # Extract functions or handle block-based code
    if student_code_type == "function_based":
        student_dict = {"functions": Utils.extract_functions(student_code)}
        teacher_dict = {"functions": Utils.extract_functions(teacher_code)}
    else:
        # For block-based code, treat the entire code as a single block
        student_dict = {"main_block": Utils.extract_main_block(student_code)}
        teacher_dict = {"main_block": Utils.extract_main_block(teacher_code)}
    
    try:
        differences = Utils.compare(student_dict, teacher_dict)
        
        conclusion = None
        if use_llm:
            try:
                conclusion = openai_client.generate_conclusion(teacher_code, student_code, differences)
            except Exception as e:
                if 'insufficient_quota' in str(e):
                    conclusion = "Analysis conclusion is currently unavailable due to API quota limitations. Please try again later or contact support."
                else:
                    conclusion = f"Error generating conclusion: {str(e)}"
        
        response = {
            'message': 'Code blocks processed successfully',
            'differences': differences,
            'conclusion': conclusion
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': 'Error processing code differences', 'details': str(e)}), 500
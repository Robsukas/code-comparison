from flask import Blueprint, request, jsonify
from lib.strict_comparison import StrictComparator
from lib.utils import Utils
from lib.gitlab_client import GitLabClient
import code_diff as cd
import textwrap

diff_bp = Blueprint('diff', __name__)
gitlab_client = GitLabClient()

@diff_bp.route('/api/diff', methods=['POST'])
def diff_endpoint():
    data = request.get_json()

    student_id = data.get('student_id')
    exercise = data.get('exercise')
    year = data.get('year')

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
    
    student_funcs_dict = Utils.extract_functions(student_code)
    teacher_funcs_dict = Utils.extract_functions(teacher_code)
    
    try:
        differences = Utils.compare(student_funcs_dict, teacher_funcs_dict)
    except Exception as e:
        return jsonify({'error': 'Error processing code differences', 'details': str(e)}), 500

    response = {
        'message': 'Code blocks processed successfully',
        'differences': differences
    }
    
    return jsonify(response), 200
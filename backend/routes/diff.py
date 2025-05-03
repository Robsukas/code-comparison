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
    data = request.get_json()

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

    # For validation, check the first file's code type
    student_code = next(iter(student_code_dict.values()))
    teacher_code = next(iter(teacher_code_dict.values()))
    
    student_code_type = Utils.detect_code_type(student_code)
    teacher_code_type = Utils.detect_code_type(teacher_code)
    
    if student_code_type != teacher_code_type:
        return jsonify({
            'error': 'Code type mismatch',
            'details': f'Student code is {student_code_type} while teacher code is {teacher_code_type}'
        }), 400
    
    diff_error = None
    llm_error  = None
    differences = None
    conclusion  = None 

    try:
        differences = Utils.compare_files(student_code_dict, teacher_code_dict)
    except Exception as e:
        diff_error = f"diff failed: {e}"
        current_app.logger.exception(diff_error)

    if use_llm:
        try:
            conclusion = ai_client.generate_conclusion(
                teacher_code_dict, student_code_dict
            )
        except Exception as e:
            llm_error = f"LLM failed: {e}"
            current_app.logger.warning(llm_error)

    return jsonify(
        message      = "ok",
        differences  = differences,   # may be None
        conclusion   = conclusion,    # may be None
        diff_error   = diff_error,    # str | None
        llm_error    = llm_error,     # str | None
    ), 200
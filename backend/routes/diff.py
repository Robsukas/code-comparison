from flask import Blueprint, request, jsonify
from lib.strict_comparison import StrictComparator
from lib.utils import Utils
import code_diff as cd
import textwrap

diff_bp = Blueprint('diff', __name__)

@diff_bp.route('/api/diff', methods=['POST'])
def diff_endpoint():
    data = request.get_json()

    student_code_block = data.get('student_code_block')
    check_code_block = data.get('check_code_block')

    student_code_block = textwrap.dedent(student_code_block or "").strip()
    check_code_block = textwrap.dedent(check_code_block or "").strip()

    if not student_code_block or not check_code_block:
        return jsonify({'error': 'Both student_code_block and check_code_block are required.'}), 400
    
    student_funcs_dict = Utils.extract_functions(student_code_block)
    check_funcs_dict = Utils.extract_functions(check_code_block)

    differences = {}

    matched_student_funcs_dict, matched_check_funcs_dict, diffs = Utils.check_function_mismatch(
        student_funcs_dict,
        check_funcs_dict
    )

    differences['function_name_mismatches'] = diffs
    
    #try:
    #    ast_comparison_result = StrictComparator.compare(code_block_1, code_block_2)
    #    code_diff_result = cd.difference(code_block_1, code_block_2, lang="python")
    #    code_diff_result_edited = code_diff_result.edit_script()
    #    code_diff_result_serializable = [str(diff) for diff in code_diff_result_edited]
    #except Exception as e:
    #    return jsonify({'error': 'Error processing code differences', 'details': str(e)}), 500

    response = {
        'message': 'Code blocks processed successfully',
        'student_functions': matched_student_funcs_dict,
        'check_functions': matched_check_funcs_dict,
        'differences': differences
    }
    
    return jsonify(response), 200
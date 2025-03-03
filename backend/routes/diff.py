from flask import Blueprint, request, jsonify
from lib.strict_comparison import StrictComparator
import code_diff as cd

diff_bp = Blueprint('diff', __name__)

@diff_bp.route('/api/diff', methods=['POST'])
def diff_endpoint():
    data = request.get_json()

    code_block_1 = data.get('code_block_1')
    code_block_2 = data.get('code_block_2')

    if not code_block_1 or not code_block_2:
        return jsonify({'error': 'Both code_block_1 and code_block_2 are required.'}), 400
    
    try:
        ast_comparison_result = StrictComparator.compare(code_block_1, code_block_2)
        code_diff_result = cd.difference(code_block_1, code_block_2, lang="python")
        code_diff_result_edited = code_diff_result.edit_script()
        code_diff_result_serializable = [str(diff) for diff in code_diff_result_edited]
    except Exception as e:
        return jsonify({'error': 'Error processing code differences', 'details': str(e)}), 500

    response = {
        'message': 'Code blocks processed successfully',
        'strict_ast_result': ast_comparison_result,
        'code_diff_result': code_diff_result_serializable
    }
    
    return jsonify(response), 200
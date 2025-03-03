from .AST_parser import ASTParser
from .AST_normalizer import ASTNormalizer
from .AST_comparator import ASTComparator


class StrictComparator:
    def compare(code_block_1, code_block_2):
        parser = ASTParser()
        normalizer = ASTNormalizer()
        comparator = ASTComparator()

        student_ast = parser.parse_code(code_block_1)
        teacher_ast = parser.parse_code(code_block_2)

        student_norm, _, _ = normalizer.normalize_ast_dict(student_ast)
        teacher_norm, _, _ = normalizer.normalize_ast_dict(teacher_ast)
        
        differences = []
        for diff in comparator.compare_ast_dicts(student_norm, teacher_norm):
            differences.append(diff)
            
        return differences

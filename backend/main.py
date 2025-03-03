import textwrap
import code_diff as cd
from lib.AST_parser import ASTParser
from lib.AST_normalizer import ASTNormalizer
from lib.AST_comparator import ASTComparator

if __name__ == "__main__":
    student_code = textwrap.dedent("""
    def is_prime_number(number: int) -> bool:
        if number <= 1:
            return False
        else:
            for i in range(2, number):
                if number % i == 0:
                    return False
        return True
    """)

    teacher_code = textwrap.dedent("""
    def is_prime_number(number: int) -> bool:
        if number == 0:
            return False
        for i in range(2, number):
            if number % i == 0:
                return False
        return True
    """)

    parser = ASTParser()
    normalizer = ASTNormalizer()
    comparator = ASTComparator()

    student_ast = parser.parse_code(student_code)
    teacher_ast = parser.parse_code(teacher_code)

    student_norm, _, _ = normalizer.normalize_ast_dict(student_ast)
    teacher_norm, _, _ = normalizer.normalize_ast_dict(teacher_ast)

    differences = comparator.compare_ast_dicts(student_norm, teacher_norm)

    code_diff = cd.difference(student_code, teacher_code, lang="python")

    print("Strict AST comparison:")
    for diff in differences:
        print(diff)

    print("\nCode diff:")
    print(code_diff.edit_script())
    

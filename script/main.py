import textwrap
from AST_parser import ASTParser
from AST_normalizer import ASTNormalizer
from AST_comparator import ASTComparator

if __name__ == "__main__":
    student_code = textwrap.dedent("""
    def clock(päevad: int, tunnid: int, minutid: int, sekundid: int):
        minutes = 0
        minutes += päevad * 1440
        minutes += tunnid * 60
        minutes += minutid
        minutes += sekundid / 60
        return minutes
    """)

    teacher_code = textwrap.dedent("""
    def clock_time(päevad: int, tunnid: int, minutid: int, sekundid: int):
        minutes = 0
        minutes += sekundid / 60
        minutes += minutid
        minutes += tunnid * 60
        minutes += päevad * 1440
        return minutes
    """)

    parser = ASTParser()
    normalizer = ASTNormalizer()
    comparator = ASTComparator()

    student_ast = parser.parse_code(student_code)
    teacher_ast = parser.parse_code(teacher_code)

    student_norm, _, _ = normalizer.normalize_ast_dict(student_ast)
    teacher_norm, _, _ = normalizer.normalize_ast_dict(teacher_ast)

    differences = comparator.compare_ast_dicts(student_norm, teacher_norm)

    if differences:
        print("Differences found:")
        for diff in differences:
            print(diff)
    else:
        print("No differences found!")

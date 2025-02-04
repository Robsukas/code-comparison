import textwrap
from AST_parser import ASTParser
from AST_normalizer import ASTNormalizer

if __name__ == "__main__":
    sample_code = textwrap.dedent("""
    def clock(päevad: int, tunnid: int, minutid: int, sekundid: int):
        minutes = 0
        minutes += päevad * 1440
        minutes += tunnid * 60
        minutes += minutid
        minutes += sekundid / 60
        return minutes
    """)

    parser = ASTParser()
    normalizer = ASTNormalizer()

    tree_dict = parser.parse_code(sample_code)
    normalized_tree_dict = normalizer.normalize_ast_dict(tree_dict)

    print("Parsed AST dictionary:\n", normalized_tree_dict)

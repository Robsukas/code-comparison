import ast


class ASTParser:
    def parse_code(self, code_str: str):
        tree = ast.parse(code_str)
        return self.convert_ast_to_dict(tree)

    def convert_ast_to_dict(self, node):
        if not isinstance(node, ast.AST):
            return node

        node_dict = {'_type': node.__class__.__name__}
        for field_name in node._fields:
            field_value = getattr(node, field_name, None)
            if isinstance(field_value, list):
                node_dict[field_name] = [self.convert_ast_to_dict(x) for x in field_value]
            else:
                node_dict[field_name] = self.convert_ast_to_dict(field_value)
        return node_dict

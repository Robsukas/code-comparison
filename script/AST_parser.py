import ast


class ASTParser:
    def parse_code(self, code_str: str):
        # Parse sample code with ast module
        tree = ast.parse(code_str)

        # Return data that has been converted to dictionary for easier understanding and functionality
        return self.convert_ast_to_dictionary(tree)

    def convert_ast_to_dictionary(self, node):
        # If lead node -> return it as it is
        if not isinstance(node, ast.AST):
            return node

        # '_type' key stores the name of the AST node class
        node_dict = {'_type': node.__class__.__name__}

        # For every field defined on the AST node, recursively convert it to dictionary
        for field_name in node._fields:

            # Get the field value via getattr, default set to None
            field_value = getattr(node, field_name, None)

            # Check field value type
            if isinstance(field_value, list):
                # If the field is a list, process each element.
                node_dict[field_name] = [self.convert_ast_to_dictionary(x) for x in field_value]
            else:
                # Otherwise, just process the single field.
                node_dict[field_name] = self.convert_ast_to_dictionary(field_value)

        return node_dict

    # GPT generated beautify print, previously returned just a oneliner, which was unreadable, this is temporary
    def print_tree(self, node_dict, indent=0):
        prefix = ' ' * (indent * 2)
        node_type = node_dict.get('_type', 'Unknown')
        print(f"{prefix}{node_type}")

        # Print fields
        for key, value in node_dict.items():
            if key == '_type':
                continue
            if isinstance(value, list):
                print(f"{prefix}  {key}:")
                for item in value:
                    if isinstance(item, dict):
                        self.print_tree(item, indent=indent + 2)
                    else:
                        print(f"{prefix}    {repr(item)}")
            elif isinstance(value, dict):
                print(f"{prefix}  {key}:")
                self.print_tree(value, indent=indent + 2)
            else:
                # Print simple fields
                print(f"{prefix}  {key}: {repr(value)}")


if __name__ == "__main__":
    # Sample code from my own Python course repository
    sample_code = """
name = input("What is your name? ")

number_1 = input("Hello, " + str(name) + "! Enter a random number: ")

number_2 = input("Great! Now enter a second random number: ")

answer = int(number_1) + int(number_2)

print(str(number_1) + " + " + str(number_2) + " is " + str(answer))
"""
    parser = ASTParser()
    tree_dict = parser.parse_code(sample_code)
    parser.print_tree(tree_dict)

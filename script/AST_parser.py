import ast
import uuid
import textwrap
from graphviz import Digraph

class ASTParser:
    def parse_code(self, code_str: str):
        # Parse sample code with ast module
        tree = ast.parse(code_str)

        # Return data that has been converted to dictionary for easier understanding and functionality
        return self.convert_ast_to_dict(tree)

    def convert_ast_to_dict(self, node):
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
                node_dict[field_name] = [self.convert_ast_to_dict(x) for x in field_value]
            else:
                # Otherwise, just process the single field.
                node_dict[field_name] = self.convert_ast_to_dict(field_value)

        return node_dict

    def convert_dict_to_graph(self, node_dict, graph=None, parent_id=None):
        """
        Recursively build a Graphviz Digraph from a nested AST dictionary.
        - node_dict: the dictionary representing an AST node
        - graph: a Digraph object (created once at the start)
        - parent_id: the unique ID of the parent node (used to create edges)
        """
        if graph is None:
            graph = Digraph(comment='AST Visualization', format='png')

        # Create a unique ID for the current node
        current_id = str(uuid.uuid4())

        # Use the '_type' key as the label for this node
        label = node_dict.get('_type', 'Unknown')
        graph.node(current_id, label)

        # If we have a parent node, connect it
        if parent_id is not None:
            graph.edge(parent_id, current_id)

        # Traverse child fields
        for key, value in node_dict.items():
            # Skip the type field itself
            if key == '_type':
                continue

            if isinstance(value, dict):
                # This is a single child node
                self.convert_dict_to_graph(value, graph, current_id)
            elif isinstance(value, list):
                # This is a list of child nodes
                for item in value:
                    if isinstance(item, dict):
                        self.convert_dict_to_graph(item, graph, current_id)
                    else:
                        # Primitive value in the list
                        leaf_id = str(uuid.uuid4())
                        leaf_label = f"{key}: {repr(item)}"
                        graph.node(leaf_id, leaf_label)
                        graph.edge(current_id, leaf_id)
            else:
                # Single primitive value
                leaf_id = str(uuid.uuid4())
                leaf_label = f"{key}: {repr(value)}"
                graph.node(leaf_id, leaf_label)
                graph.edge(current_id, leaf_id)

        return graph


if __name__ == "__main__":
    # Sample code from my own Python course repository
    sample_code = textwrap.dedent("""
        def find_id_code(text: str) -> str:
            result = ""
            for i in range(len(text)):
                char = text[i]
                if char.isdigit():
                    result += char
            if len(result) > 11:
                return "Too many numbers!"
            elif len(result) < 11:
                return "Not enough numbers!"
            return result
    """)
    parser = ASTParser()
    tree_dict = parser.parse_code(sample_code)
    ast_graph = parser.convert_dict_to_graph(tree_dict)
    ast_graph.render('ast_graph', view=True)

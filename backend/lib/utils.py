import ast

class Utils:

    @staticmethod
    def extract_functions(source_code: str) -> dict:
        """
        Parse the code, remove comments and docstrings,
        and return a dict mapping function_name -> function_source.
        """
        # 1. Parse to AST
        tree = ast.parse(source_code)

        # 2. Prepare a dict for extracted functions
        functions_dict = {}

        # 3. Walk the AST to find all FunctionDef (and maybe AsyncFunctionDef)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Remove the docstring if present
                if (node.body and 
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, (ast.Constant))):
                    # Remove the first node (docstring)
                    node.body.pop(0)

                # Re-unparse the node back into source
                fn_source = ast.unparse(node)
                functions_dict[node.name] = fn_source

        return functions_dict
    
    @staticmethod
    def check_function_mismatch(student_dict: dict, check_dict: dict):
        """
        Compare the two function dictionaries by name to see if there is any mismatches.

        Returns:
            matched_in_student (dict): subset of student_funcs that also exist in check_funcs
            matched_in_check   (dict): subset of check_funcs that also exist in student_funcs
            differences_list   (list of strings): textual explanations about missing/extra functions
        """
        matched_in_student = {}
        matched_in_check = {}
        differences_list = []

        # Check every function in the student code
        for fn_name, fn_code in student_dict.items():
            if fn_name in check_dict:
                # function present in both
                matched_in_student[fn_name] = fn_code
                matched_in_check[fn_name] = check_dict[fn_name]
            else:
                # function is in student code, but missing from check code
                differences_list.append(
                    f"Function '{fn_name}' is in student code but missing in check code."
                )

        # Check if there are leftover functions in the check code that are not in the student code
        for fn_name in check_dict.keys():
            if fn_name not in student_dict:
                differences_list.append(
                    f"Function '{fn_name}' is in check code but missing in student code."
                )

        return matched_in_student, matched_in_check, differences_list


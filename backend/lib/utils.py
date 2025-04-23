import ast
from pyflowchart import Flowchart
from .strict_comparison import StrictComparator
from .structural_comparison import StructuralComparator

class Utils:

    @staticmethod
    def extract_functions(source_code: str) -> dict:
        tree = ast.parse(source_code)
        functions_dict = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if (node.body and 
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, (ast.Constant))):
                    node.body.pop(0)
                fn_source = ast.unparse(node)
                functions_dict[node.name] = fn_source
        return functions_dict

    @staticmethod
    def check_function_mismatch(student_dict: dict, check_dict: dict):
        matched_in_student = {}
        matched_in_check = {}
        differences_list = []
        for fn_name, fn_code in student_dict.items():
            if fn_name in check_dict:
                matched_in_student[fn_name] = fn_code
                matched_in_check[fn_name] = check_dict[fn_name]
            else:
                differences_list.append(
                    f"Function '{fn_name}' is in student code but missing in check code."
                )
        for fn_name in check_dict.keys():
            if fn_name not in student_dict:
                differences_list.append(
                    f"Function '{fn_name}' is in check code but missing in student code."
                )
        return matched_in_student, matched_in_check, differences_list

    @staticmethod
    def generate_unified_diff(student_code: str, teacher_code: str, func_name: str) -> str:
        """Generate a unified diff string for the given student and teacher code."""
        from difflib import unified_diff
        student_lines = student_code.splitlines(keepends=True)
        teacher_lines = teacher_code.splitlines(keepends=True)
        
        # Generate unified diff
        diff_lines = list(unified_diff(
            student_lines,
            teacher_lines,
            fromfile=f'a/{func_name}.py',
            tofile=f'b/{func_name}.py',
            lineterm=''
        ))
        
        return '\n'.join(diff_lines)

    @staticmethod
    def compare(student_funcs: dict, teacher_funcs: dict) -> dict:
        result = {}
        for func_name, student_code in student_funcs.items():
            if func_name in teacher_funcs:
                teacher_code = teacher_funcs[func_name]

                strict_comparison = StrictComparator.compare(student_code, teacher_code)

                structural_info = StructuralComparator.compare(student_code, teacher_code)
                
                unified_diff = Utils.generate_unified_diff(student_code, teacher_code, func_name)

                result[func_name] = {
                    "strict_comparison": strict_comparison,
                    "teacherDSL": structural_info["teacherDSL"],
                    "studentDSL": structural_info["studentDSL"],
                    "unified_diff": unified_diff
                }
        _, _, mismatches = Utils.check_function_mismatch(student_funcs, teacher_funcs)
        final_result = {
            "module_specific_diffs": {"function_mismatch": mismatches},
            "function_specific_diffs": result
        }
        return final_result

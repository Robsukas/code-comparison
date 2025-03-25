import ast
import code_diff as cd
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
    def compare(student_funcs: dict, teacher_funcs: dict) -> dict:
        result = {}
        for func_name, student_code in student_funcs.items():
            if func_name in teacher_funcs:
                teacher_code = teacher_funcs[func_name]
                
                strict_comparison = StrictComparator.compare(student_code, teacher_code)
                diff = cd.difference(student_code, teacher_code, lang="python")
                code_diff_result = [str(instr) for instr in diff.edit_script()]
                
                structural_info = StructuralComparator.compare(student_code, teacher_code)
                
                result[func_name] = {
                    "strict_comparison": strict_comparison,
                    "code_diff": code_diff_result,
                    "teacherDSL": structural_info["teacherDSL"],
                    "studentDSL": structural_info["studentDSL"]
                }
        # might use matched_in_student and matched_in_check later
        _, _, mismatches = Utils.check_function_mismatch(student_funcs, teacher_funcs)
        final_result = {
            "module_specific_diffs": {
                "function_mismatch": mismatches
            },
            "function_specific_diffs": result
        }
        return final_result

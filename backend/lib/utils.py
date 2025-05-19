"""
Code Analysis and Comparison Utilities

This module provides utility functions for analyzing and comparing Python code,
supporting both function-based and block-based code structures. It includes
functionality for:
- Code type detection (function-based vs block-based)
- Function extraction and comparison
- Main block extraction
- Unified diff generation
- File comparison with support for different naming conventions

The module integrates with StrictComparator and StructuralComparator for
detailed code analysis and comparison.

Dependencies:
    - ast: For Python code parsing and analysis
    - pyflowchart: For structural code analysis
    - difflib: For generating unified diffs
"""

import ast
from pyflowchart import Flowchart
from .strict_comparison import StrictComparator
from .structural_comparison import StructuralComparator


class Utils:
    """
    Utility class for code analysis and comparison operations.
    
    This class provides static methods for various code analysis tasks,
    including code type detection, function extraction, and comparison
    of both function-based and block-based code structures.
    """

    @staticmethod
    def detect_code_type(source_code: str) -> str:
        """
        Detect whether the code is function-based or block-based.
        
        Args:
            source_code (str): The source code to analyze
            
        Returns:
            str: Either "function_based" or "block_based"
            
        Note:
            Returns "block_based" if the code contains syntax errors
            or if no functions are found.
        """
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return "function_based"
            return "block_based"
        except SyntaxError:
            return "block_based"  # If code can't be parsed, treat it as a block

    @staticmethod
    def extract_functions(source_code: str) -> dict:
        """
        Extract all functions from the source code.
        
        Args:
            source_code (str): The source code to extract functions from
            
        Returns:
            dict: Dictionary mapping function names to their source code
            
        Note:
            Removes docstrings from the extracted functions.
        """
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
    def _is_doc_expr(node: ast.AST) -> bool:
        """
        Check if an AST node is a docstring expression.
        
        Args:
            node (ast.AST): The AST node to check
            
        Returns:
            bool: True if the node is a docstring expression
        """
        return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)   # ast.Str on < 3.8
            and isinstance(node.value.value, str)
        )

    @staticmethod
    def extract_main_block(source_code: str) -> str:
        """
        Extract the main block of code, removing docstrings.
        
        Args:
            source_code (str): The source code to process
            
        Returns:
            str: The main block of code with docstrings removed
            
        Note:
            Removes docstrings from:
            - Module level
            - Function definitions
            - Class definitions
        """
        try:
            tree = ast.parse(source_code)

            while tree.body and Utils._is_doc_expr(tree.body[0]):
                tree.body.pop(0)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef,
                                      ast.AsyncFunctionDef,
                                      ast.ClassDef)):
                    if node.body and Utils._is_doc_expr(node.body[0]):
                        node.body.pop(0)

            tree.body = [n for n in tree.body if not Utils._is_doc_expr(n)]

            return ast.unparse(tree)

        except SyntaxError:
            return source_code

    @staticmethod
    def check_function_mismatch(student_dict: dict, check_dict: dict):
        """
        Check for mismatches between student and teacher functions.
        
        Args:
            student_dict (dict): Dictionary of student's functions
            check_dict (dict): Dictionary of teacher's functions
            
        Returns:
            tuple: (matched_student_funcs, matched_teacher_funcs, differences_list)
                where differences_list contains messages about missing functions
        """
        matched_in_student = {}
        matched_in_check = {}
        differences_list = []
        for fn_name, fn_code in student_dict.items():
            if fn_name in check_dict:
                matched_in_student[fn_name] = fn_code
                matched_in_check[fn_name] = check_dict[fn_name]
            else:
                differences_list.append(
                    f"Function '{fn_name}' is in student code but missing in teacher code."
                )
        for fn_name in check_dict.keys():
            if fn_name not in student_dict:
                differences_list.append(
                    f"Function '{fn_name}' is in teacher code but missing in student code."
                )
        return matched_in_student, matched_in_check, differences_list

    @staticmethod
    def generate_unified_diff(student_code: str, teacher_code: str, func_name: str) -> str:
        """
        Generate a unified diff between student and teacher code.
        
        Args:
            student_code (str): Student's code
            teacher_code (str): Teacher's code
            func_name (str): Name of the function or block being compared
            
        Returns:
            str: Unified diff in standard format
        """
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
    def compare(student_dict: dict, teacher_dict: dict) -> dict:
        """
        Compare student and teacher code using multiple comparison methods.
        
        This method performs:
        - Strict comparison (AST-based)
        - Structural comparison (flowchart-based)
        - Unified diff generation
        - Function mismatch detection
        
        Args:
            student_dict (dict): Student's code dictionary
            teacher_dict (dict): Teacher's code dictionary
            
        Returns:
            dict: Comparison results including:
                - module_specific_diffs: Function mismatches
                - function_specific_diffs: Detailed comparisons for each function/block
        """
        result = {}
        
        # Check if we're comparing block-based code
        is_block_based = "main" in student_dict or "main" in teacher_dict
        
        if is_block_based:
            # For block-based code, compare the entire blocks
            student_code = student_dict.get("main", "")
            teacher_code = teacher_dict.get("main", "")
            
            strict_comparison = StrictComparator.compare(student_code, teacher_code)
            structural_info = StructuralComparator.compare(student_code, teacher_code)
            unified_diff = Utils.generate_unified_diff(student_code, teacher_code, "main")
            
            result["main"] = {
                "strict_comparison": strict_comparison,
                "unifiedDSL": structural_info["unifiedDSL"],
                "structuralComparison": structural_info["structural_error"],
                "unified_diff": unified_diff
            }
            
            # No function mismatches for block-based code
            mismatches = []
        else:
            # For function-based code, compare each function
            student_funcs = student_dict.get("functions", {})
            teacher_funcs = teacher_dict.get("functions", {})
            
            for func_name, student_code in student_funcs.items():
                if func_name in teacher_funcs:
                    teacher_code = teacher_funcs[func_name]
                    
                    strict_comparison = StrictComparator.compare(student_code, teacher_code)
                    structural_info = StructuralComparator.compare(student_code, teacher_code)
                    unified_diff = Utils.generate_unified_diff(student_code, teacher_code, func_name)
                    
                    result[func_name] = {
                        "strict_comparison": strict_comparison,
                        "unifiedDSL": structural_info["unifiedDSL"],
                        "structuralComparison": structural_info["structural_error"],
                        "unified_diff": unified_diff
                    }
            
            # Check for function mismatches using the existing method
            _, _, mismatches = Utils.check_function_mismatch(student_funcs, teacher_funcs)
        
        return {
            "module_specific_diffs": {"function_mismatch": mismatches},
            "function_specific_diffs": result
        }

    @staticmethod
    def extract_functions_from_files(files_dict: dict) -> dict:
        """
        Extract functions from multiple files.
        
        Args:
            files_dict (dict): Dictionary mapping filenames to source code
            
        Returns:
            dict: Dictionary mapping filenames to their function dictionaries
        """
        result = {}
        for filename, code in files_dict.items():
            result[filename] = Utils.extract_functions(code)
        return result

    @staticmethod
    def extract_main_blocks_from_files(files_dict: dict) -> dict:
        """
        Extract main blocks from multiple files.
        
        Args:
            files_dict (dict): Dictionary mapping filenames to source code
            
        Returns:
            dict: Dictionary mapping filenames to their main blocks
        """
        result = {}
        for filename, code in files_dict.items():
            result[filename] = {"main": Utils.extract_main_block(code)}
        return result

    @staticmethod
    def compare_files(student_files: dict, teacher_files: dict) -> dict:
        """
        Compare multiple student files against teacher files.
        
        This method:
        1. Maps student files to corresponding teacher files
        2. Detects code type for each file
        3. Performs appropriate comparison based on code type
        4. Aggregates results across all files
        
        Args:
            student_files (dict): Dictionary of student's files
            teacher_files (dict): Dictionary of teacher's files
            
        Returns:
            dict: Comparison results including:
                - module_specific_diffs: Function mismatches across all files
                - function_specific_diffs: Detailed comparisons for each file
        """
        result = {
            "module_specific_diffs": {
                "function_mismatch": []
            },
            "function_specific_diffs": {}
        }
        
        # Create a mapping of student filenames to teacher filenames
        filename_mapping = {}
        for student_filename in student_files.keys():
            # Try to find matching teacher file by removing _solution suffix
            base_name = student_filename.replace('_solution.py', '.py')
            if base_name in teacher_files:
                filename_mapping[student_filename] = base_name
            else:
                # If no exact match, try to find a file with the same base name
                for teacher_filename in teacher_files.keys():
                    if teacher_filename.replace('_solution.py', '.py') == base_name:
                        filename_mapping[student_filename] = teacher_filename
                        break
        
        # Compare files using the mapping
        for student_filename, teacher_filename in filename_mapping.items():
            student_code = student_files[student_filename]
            teacher_code = teacher_files[teacher_filename]
            
            # Detect code type
            is_function_based = Utils.detect_code_type(student_code) == "function_based"
            
            if is_function_based:
                # Extract functions from both files
                student_funcs = Utils.extract_functions(student_code)
                teacher_funcs = Utils.extract_functions(teacher_code)
                
                # Compare functions
                comparison = Utils.compare(
                    {"functions": student_funcs},
                    {"functions": teacher_funcs}
                )
                
                # Add mismatches to top level
                result["module_specific_diffs"]["function_mismatch"].extend(
                    comparison["module_specific_diffs"]["function_mismatch"]
                )
                
                # Add function comparisons under filename
                result["function_specific_diffs"][student_filename] = comparison["function_specific_diffs"]
            else:
                # Extract main blocks from both files
                student_block = Utils.extract_main_block(student_code)
                teacher_block = Utils.extract_main_block(teacher_code)
                
                # Compare blocks
                comparison = Utils.compare(
                    {"main": student_block},
                    {"main": teacher_block}
                )
                
                # Add function comparisons under filename
                result["function_specific_diffs"][student_filename] = comparison["function_specific_diffs"]
        
        return result


"""
Structural Code Comparison Module

This module provides functionality for comparing the structural flow of student and
teacher code by converting them into flowcharts and analyzing their differences.
It uses a color-coded system to highlight various types of differences:

Color Flags:
    - diff_teacher_only (blue): Code present only in teacher's solution
    - diff_student_only (red): Code present only in student's solution
    - diff_replace (orange): Major differences in node labels (marked with Δ)
    - diff_edit (yellow): Minor differences in node labels (marked with ✎)

The comparison is performed by:
1. Converting both code samples to flowchart DSL
2. Extracting and comparing node structures
3. Identifying differences using sequence matching
4. Generating a unified DSL with color flags

Dependencies:
    - difflib: For sequence comparison
    - pyflowchart: For converting code to flowchart DSL
    - re: For regular expression matching
"""

import re
from difflib import SequenceMatcher, ndiff
from pyflowchart import Flowchart


class StructuralComparator:
    """
    Compares the structural flow of student and teacher code using flowcharts.
    
    This class implements a two-pass comparison algorithm that:
    1. First identifies structural differences using sequence matching
    2. Then refines the comparison to handle different types of changes
    3. Finally generates a unified flowchart DSL with color-coded differences
    
    The comparison focuses on both the structure (node types and connections)
    and the content (node labels) of the flowcharts.
    """

    @staticmethod
    def extract_node_type(line: str) -> str:
        """
        Extract the node type from a flowchart DSL line.
        
        Args:
            line (str): A line from the flowchart DSL
            
        Returns:
            str: The node type (e.g., 'operation', 'condition', 'output')
        """
        m = re.search(r'=>\s*([^:]+)', line)
        return m.group(1).strip() if m else ""

    @staticmethod
    def extract_node_label(line: str) -> str:
        """
        Extract the node label from a flowchart DSL line.
        
        Args:
            line (str): A line from the flowchart DSL
            
        Returns:
            str: The node label (content before any flags)
        """
        return line.split(':', 1)[1].split('|', 1)[0]

    @staticmethod
    def extract_node_id(line: str) -> str:
        """
        Create a unique identifier for a node combining type and label.
        
        Args:
            line (str): A line from the flowchart DSL
            
        Returns:
            str: Node identifier in format "type|label" (label truncated to 30 chars)
        """
        typ   = StructuralComparator.extract_node_type(line)
        label = StructuralComparator.extract_node_label(line)
        return f"{typ}|{label[:30].strip()}"

    @staticmethod
    def split_nodes(dsl: str):
        """
        Split flowchart DSL into nodes and other elements.
        
        Args:
            dsl (str): The flowchart DSL string
            
        Returns:
            tuple: (nodes, other) where:
                - nodes: List of (line, node_id) tuples
                - other: List of non-node lines (connections, etc.)
        """
        nodes, other = [], []
        for ln in dsl.splitlines():
            ln = ln.strip()
            if '=>' in ln:
                nodes.append((ln, StructuralComparator.extract_node_id(ln)))
            else:
                other.append(ln)
        return nodes, other

    @staticmethod
    def first_pass(t_ids, s_ids):
        """
        Perform initial sequence comparison between teacher and student nodes.
        
        Args:
            t_ids (list): List of teacher node identifiers
            s_ids (list): List of student node identifiers
            
        Returns:
            list: SequenceMatcher opcodes describing the differences
        """
        return SequenceMatcher(a=t_ids, b=s_ids, autojunk=False).get_opcodes()

    @staticmethod
    def refine_replace_spans(opcodes, t_nodes, s_nodes):
        """
        Refine the comparison by analyzing node types within replace operations.
        
        This method looks at the node types within replace operations to better
        understand the nature of the changes and potentially split them into
        smaller, more specific differences.
        
        Args:
            opcodes (list): Original sequence comparison opcodes
            t_nodes (list): Teacher nodes
            s_nodes (list): Student nodes
            
        Returns:
            list: Refined opcodes with more detailed difference information
        """
        refined = []
        for tag, t_lo, t_hi, s_lo, s_hi in opcodes:
            if tag != "replace":
                refined.append((tag, t_lo, t_hi, s_lo, s_hi))
                continue

            typ_a = [n[1].split('|', 1)[0] for n in t_nodes[t_lo:t_hi]]
            typ_b = [n[1].split('|', 1)[0] for n in s_nodes[s_lo:s_hi]]

            for sub in SequenceMatcher(a=typ_a, b=typ_b,
                                       autojunk=False).get_opcodes():
                st, a0, a1, b0, b1 = sub
                refined.append((st, t_lo+a0, t_lo+a1, s_lo+b0, s_lo+b1))
        return refined

    @staticmethod
    def compare(student_code: str, teacher_code: str) -> dict:
        """
        Compare student and teacher code by converting to flowcharts.
        
        Args:
            student_code (str): Student's code to check
            teacher_code (str): Teacher's reference code
            
        Returns:
            dict: Contains:
                - unifiedDSL: Combined flowchart DSL with difference flags
                - structural_error: Error message if comparison fails
        """
        try:
            t_flow = Flowchart.from_code(teacher_code).flowchart()
            s_flow = Flowchart.from_code(student_code).flowchart()
        except Exception as e:
            return {"unifiedDSL": "", "structural_error": str(e)}

        t_nodes, t_other = StructuralComparator.split_nodes(t_flow)
        s_nodes, _       = StructuralComparator.split_nodes(s_flow)

        first   = StructuralComparator.first_pass(
                     [n[1] for n in t_nodes], [n[1] for n in s_nodes])
        opcodes = StructuralComparator.refine_replace_spans(first,
                                                            t_nodes, s_nodes)

        unified = StructuralComparator.merged_dsl(opcodes,
                                                  t_nodes, s_nodes, t_other)
        return {"unifiedDSL": unified, "structural_error": None}

    @staticmethod
    def merged_dsl(opcodes, t_nodes, s_nodes, t_other):
        """
        Generate unified flowchart DSL with difference flags.
        
        This method combines the teacher and student flowcharts into a single
        DSL, marking differences with appropriate color flags and symbols.
        
        Args:
            opcodes (list): Refined comparison opcodes
            t_nodes (list): Teacher nodes
            s_nodes (list): Student nodes
            t_other (list): Other elements from teacher's flowchart
            
        Returns:
            str: Unified flowchart DSL with difference markers
        """
        out = []

        def flag(line, suf):
            """Add a difference flag to a node line."""
            return f"{line.split('|',1)[0]}|{suf}"

        def small_edit(a: str, b: str) -> bool:
            """
            Determine if the difference between labels is minor.
            
            A difference is considered minor if:
            - The number of character differences is <= 4, or
            - The difference ratio is <= 25%
            """
            if not a or not b:
                return False
            diff = sum(1 for c in ndiff(a, b) if c[0] in "-+")
            return diff <= 4 or diff / max(len(a), len(b)) <= 0.25

        def overlay(t_line, s_line):
            """
            Create a combined node showing both teacher and student versions.
            
            Returns a node with:
            - Original node type
            - Both teacher and student labels
            - Appropriate difference flag and symbol
            """
            teacher_lbl = StructuralComparator.extract_node_label(t_line).strip()
            student_lbl = StructuralComparator.extract_node_label(s_line).strip()

            base = t_line.split(":", 1)[0]            # 'op8=>output'

            if small_edit(teacher_lbl, student_lbl):
                # yellow
                glyph = "✎"
                flag  = "diff_edit"
            else:
                # orange
                glyph = "Δ"
                flag  = "diff_replace"

            body = (
                f"teacher: {teacher_lbl}\n"
                f"{glyph}\n"
                f"student: {student_lbl}"
            )

            return f"{base}: {body}|{flag}"

        # Process each difference operation
        for tag, t_lo, t_hi, s_lo, s_hi in opcodes:
            if tag == "equal":
                out.extend(t_nodes[i][0] for i in range(t_lo, t_hi))

            elif tag == "replace":
                for i, j in zip(range(t_lo, t_hi), range(s_lo, s_hi)):
                    out.append(overlay(t_nodes[i][0], s_nodes[j][0]))
                for i in range(i + 1, t_hi):
                    out.append(flag(t_nodes[i][0], "diff_teacher_only"))
                for j in range(j + 1, s_hi):
                    out.append(flag(s_nodes[j][0], "diff_student_only"))

            elif tag == "delete":
                for i in range(t_lo, t_hi):
                    out.append(flag(t_nodes[i][0], "diff_teacher_only"))

            elif tag == "insert":
                for j in range(s_lo, s_hi):
                    out.append(flag(s_nodes[j][0], "diff_student_only"))

        out.extend(t_other)
        return "\n".join(out)

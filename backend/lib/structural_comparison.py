import re
from pyflowchart import Flowchart

class StructuralComparator:
    @staticmethod
    def compare(student_code: str, teacher_code: str) -> dict:
        try:
            teacher_flow = Flowchart.from_code(teacher_code).flowchart()
        except Exception as e:
            teacher_flow = f"Error generating teacher flowchart: {e}"
        try:
            student_flow = Flowchart.from_code(student_code).flowchart()
        except Exception as e:
            student_flow = f"Error generating student flowchart: {e}"

        teacher_dsl_lines = teacher_flow.splitlines()
        student_dsl_lines = student_flow.splitlines()

        teacher_nodes, teacher_other = StructuralComparator.extract_nodes_and_other(teacher_dsl_lines)
        student_nodes, student_other = StructuralComparator.extract_nodes_and_other(student_dsl_lines)

        teacher_nodes_flagged, student_nodes_flagged = StructuralComparator.compare_by_type_in_order(
            teacher_nodes, student_nodes
        )

        teacher_dsl_with_flags = StructuralComparator.rebuild_dsl(
            teacher_nodes_flagged, teacher_other
        )
        student_dsl_with_flags = StructuralComparator.rebuild_dsl(
            student_nodes_flagged, student_other
        )

        return {
            "teacherDSL": teacher_dsl_with_flags,
            "studentDSL": student_dsl_with_flags
        }

    @staticmethod
    def extract_nodes_and_other(lines):
        nodes = []
        other = []
        for line in lines:
            trimmed = line.strip()
            if '=>' in trimmed:
                node_type = StructuralComparator.extract_node_type(trimmed)
                nodes.append((trimmed, node_type))
            else:
                other.append(trimmed)
        return nodes, other

    @staticmethod
    def extract_node_type(node_line):
        match = re.search(r'=>([^:]+)', node_line)
        if match:
            return match.group(1).strip()
        return ""  # fallback if no match

    @staticmethod
    def compare_by_type_in_order(teacher_nodes, student_nodes):
        i = 0
        t_len = len(teacher_nodes)
        s_len = len(student_nodes)

        teacher_nodes_flagged = list(teacher_nodes)
        student_nodes_flagged = list(student_nodes)

        while i < max(t_len, s_len):
            if i < t_len and i < s_len:
                teacher_type = teacher_nodes_flagged[i][1]
                student_type = student_nodes_flagged[i][1]

                if teacher_type != student_type:
                    teacher_line = teacher_nodes_flagged[i][0]
                    student_line = student_nodes_flagged[i][0]

                    if '|teacher_extra' not in teacher_line:
                        teacher_line += '|teacher_extra'
                    if '|student_extra' not in student_line:
                        student_line += '|student_extra'

                    teacher_nodes_flagged[i] = (teacher_line, teacher_type)
                    student_nodes_flagged[i] = (student_line, student_type)
            else:
                if i < t_len:
                    t_line, t_type = teacher_nodes_flagged[i]
                    if '|teacher_extra' not in t_line:
                        t_line += '|teacher_extra'
                    teacher_nodes_flagged[i] = (t_line, t_type)
                if i < s_len:
                    s_line, s_type = student_nodes_flagged[i]
                    if '|student_extra' not in s_line:
                        s_line += '|student_extra'
                    student_nodes_flagged[i] = (s_line, s_type)

            i += 1

        return teacher_nodes_flagged, student_nodes_flagged

    @staticmethod
    def rebuild_dsl(flagged_nodes, other_lines):
        lines = []
        for (line, _) in flagged_nodes:
            lines.append(line)
        for item in other_lines:
            lines.append(item)
        return "\n".join(lines)

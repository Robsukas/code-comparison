import re
from difflib import SequenceMatcher, ndiff
from pyflowchart import Flowchart


class StructuralComparator:
    """
    Build ONE Flowchart-DSL with four colour flags
        diff_teacher_only   blue
        diff_student_only   red
        diff_replace        orange - big label diff  (Δ prefix)
        diff_edit           yellow - small label diff (✎ prefix)
    """

    @staticmethod
    def extract_node_type(line: str) -> str:
        m = re.search(r'=>\s*([^:]+)', line)
        return m.group(1).strip() if m else ""

    @staticmethod
    def extract_node_label(line: str) -> str:
        return line.split(':', 1)[1].split('|', 1)[0]

    @staticmethod
    def extract_node_id(line: str) -> str:
        typ   = StructuralComparator.extract_node_type(line)
        label = StructuralComparator.extract_node_label(line)
        return f"{typ}|{label[:30].strip()}"

    @staticmethod
    def split_nodes(dsl: str):
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
        return SequenceMatcher(a=t_ids, b=s_ids, autojunk=False).get_opcodes()

    @staticmethod
    def refine_replace_spans(opcodes, t_nodes, s_nodes):
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
        out = []

        def flag(line, suf):
            return f"{line.split('|',1)[0]}|{suf}"

        def small_edit(a: str, b: str) -> bool:
            if not a or not b:
                return False
            diff = sum(1 for c in ndiff(a, b) if c[0] in "-+")
            return diff <= 4 or diff / max(len(a), len(b)) <= 0.25

        def overlay(t_line, s_line):
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

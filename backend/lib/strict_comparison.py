from __future__ import annotations

import ast
from dataclasses import dataclass
from itertools import zip_longest
from typing import List, Literal

@dataclass
class _DiffEntry:
    category: str                         # Operator | Literal | …
    location: str                         # "line 8"
    teacher: str                          # snippet
    student: str                          # snippet
    message: str                          # human sentence
    severity: Literal["info", "warning", "error"]

    ICON = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}

    def to_line(self) -> str:
        icon = self.ICON[self.severity]

        gap_icon = "\u00A0" * 2

        loc_raw  = f"‹{self.location}›"
        COL_WIDTH = 12
        pad_len = max(0, COL_WIDTH - len(loc_raw))
        loc_pad = "\u00A0" * pad_len

        gap_after_loc = "\u00A0" * 2

        return f"{icon}{gap_icon}{loc_raw}{loc_pad}{gap_after_loc}{self.message}"



class StrictComparator:
    @staticmethod
    def _lineno(node: ast.AST, fallback: str | None = None) -> str:
        return str(getattr(node, "lineno", fallback if fallback is not None else "?"))

    @staticmethod
    def _snippet(src: str, node: ast.AST) -> str:
        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
            lines = src.splitlines()
            lo = max(node.lineno - 1, 0)
            hi = min(node.end_lineno, len(lines))
            return "\n".join(lines[lo:hi]).strip()

        try:
            return ast.unparse(node).strip()
        except Exception:
            return str(node)

    @classmethod
    def _diff_nodes(
        cls,
        a: ast.AST,
        b: ast.AST,
        a_src: str,
        b_src: str,
        out: list[_DiffEntry],
        current_line: str | None = None,
    ) -> None:
        my_line = cls._lineno(a, fallback=current_line)

        if type(a) is not type(b):
            out.append(
                _DiffEntry(
                    category="NodeType",
                    location=f"line {my_line}",
                    teacher=cls._snippet(a_src, a),
                    student=cls._snippet(b_src, b),
                    message=f"{type(a).__name__} replaced by {type(b).__name__}",
                    severity="error",
                )
            )
            return

        if isinstance(a, ast.Compare) and a.ops and b.ops:
            op_a = a.ops[0].__class__.__name__
            op_b = b.ops[0].__class__.__name__
            if op_a != op_b:
                out.append(
                    _DiffEntry(
                        category="Operator",
                        location=f"line {my_line}",
                        teacher=cls._snippet(a_src, a),
                        student=cls._snippet(b_src, b),
                        message=f"Condition operator changed ({op_a} → {op_b})",
                        severity="warning",
                    )
                )

        if isinstance(a, ast.Constant) and a.value != getattr(b, "value", None):
            out.append(
                _DiffEntry(
                    category="Literal",
                    location=f"line {my_line}",
                    teacher=repr(a.value),
                    student=repr(getattr(b, "value", None)),
                    message=f"Literal value changed ({a.value!r} → {b.value!r})",
                    severity="warning",
                )
            )

        if (
            isinstance(a, ast.Call)
            and isinstance(b, ast.Call)
            and isinstance(a.func, ast.Name)
            and isinstance(b.func, ast.Name)
            and a.func.id != b.func.id
        ):
            out.append(
                _DiffEntry(
                    category="Call",
                    location=f"line {my_line}",
                    teacher=a.func.id,
                    student=b.func.id,
                    message=f"Function call renamed ({a.func.id} → {b.func.id})",
                    severity="error",
                )
            )

        for field in a._fields:
            ca, cb = getattr(a, field, None), getattr(b, field, None)

            if isinstance(ca, list) and isinstance(cb, list):
                for xa, xb in zip_longest(ca, cb, fillvalue=None):
                    if xa is None or xb is None:
                        missing = "teacher" if xa is None else "student"
                        node = xb if xa is None else xa
                        out.append(
                            _DiffEntry(
                                category="MissingNode",
                                location=f"line {cls._lineno(node, fallback=my_line)}",
                                teacher=cls._snippet(a_src, node)
                                if missing == "student"
                                else "",
                                student=cls._snippet(b_src, node)
                                if missing == "teacher"
                                else "",
                                message=f"Statement present only in {missing} code",
                                severity="error",
                            )
                        )
                    elif isinstance(xa, ast.AST):
                        cls._diff_nodes(
                            xa, xb, a_src, b_src, out, current_line=my_line
                        )

            elif isinstance(ca, ast.AST) and isinstance(cb, ast.AST):
                cls._diff_nodes(ca, cb, a_src, b_src, out, current_line=my_line)

            else:
                if ca != cb and field in ("id", "arg", "attr"):
                    out.append(
                        _DiffEntry(
                            category="Identifier",
                            location=f"line {my_line}",
                            teacher=str(ca),
                            student=str(cb),
                            message=f"Identifier changed ({ca} → {cb})",
                            severity="info",
                        )
                    )


    @classmethod
    def compare(cls, student_code: str, teacher_code: str) -> List[str]:
        try:
            s_tree = ast.parse(student_code)
            t_tree = ast.parse(teacher_code)
        except SyntaxError as exc:
            return [f"❌ Syntax error while parsing code: {exc}"]

        diffs: list[_DiffEntry] = []
        cls._diff_nodes(
            s_tree, t_tree, student_code, teacher_code, diffs, current_line=None
        )

        if not diffs:
            return ["✔ No structural differences detected."]

        seen, lines = set(), []
        for d in diffs:
            line = d.to_line()
            if line not in seen:
                seen.add(line)
                lines.append(line)
        return lines

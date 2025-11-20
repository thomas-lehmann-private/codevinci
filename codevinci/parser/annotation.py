"""Module annotation with parser for detecting types."""

import ast
from typing import List, Tuple


class AnnotationParser:
    """Parser for parsing types."""

    @staticmethod
    def resolve(node: ast.AST) -> Tuple[str, List[str]]:
        """
        Convert a type-hint AST node into a readable string and return a list of referenced names.
        Covers all real-world annotation types: Name, Constant, Attribute, Subscript, Tuple.
        """
        # Name: str, Demo, int
        if isinstance(node, ast.Name):
            return (node.id, [node.id])

        # Forward reference: 'Demo'
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return (node.value, [node.value])

        # None, True, False (older Pythons used NameConstant)
        if isinstance(node, ast.Constant):
            return (repr(node.value), [])

        # Attribute: typing.List, module.Class
        if isinstance(node, ast.Attribute):
            base, names = AnnotationParser.resolve(node.value)
            full = f"{base}.{node.attr}" if base else node.attr
            return (full, names + [node.attr])

        # Subscript: list[X], dict[K, V]
        if isinstance(node, ast.Subscript):
            base, base_names = AnnotationParser.resolve(node.value)

            # Handle python ≤3.8: Index wrapper
            slice_node = node.slice
            if hasattr(ast, "Index") and isinstance(slice_node, ast.Index):
                slice_node = slice_node.value

            # Tuple inside subscript: dict[K, V]
            if isinstance(slice_node, ast.Tuple):
                parts = []
                names = base_names[:]
                for elt in slice_node.elts:
                    t, n = AnnotationParser.resolve(elt)
                    parts.append(t)
                    names.extend(n)
                return (f"{base}[{', '.join(parts)}]", names)

            # Single type parameter: list[X]
            sub_str, sub_names = AnnotationParser.resolve(slice_node)
            return (f"{base}[{sub_str}]", base_names + sub_names)

        # Fallback: use ast.unparse
        try:
            text = ast.unparse(node)
        except Exception:
            text = "<unknown>"

        return (text, [])

"""Module tools."""

import ast
from typing import Any, Generator, Tuple

from codevinci.files import Files


class ParserTools:
    """Hilfstool zum Erstellen eines Parsers aus einer Datei."""

    @staticmethod
    def from_file(path: str) -> Any:
        """Parse AST for a given file."""
        with open(path, "r", encoding="utf-8") as handle:
            return ast.parse(handle.read(), filename=path)

    @staticmethod
    def find_all_classes(path: str) -> Generator[Tuple[str, ast.ClassDef], None, None]:
        """Find all classes for given package path."""
        for file in Files.scan(path):
            tree = ParserTools.from_file(file)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    yield file, node

    @staticmethod
    def find_all_methods(node: ast.ClassDef) -> Generator[ast.FunctionDef, None, None]:
        """Find all methods for an AST class node."""
        for child_node in ast.iter_child_nodes(node):
            if isinstance(child_node, ast.FunctionDef):
                yield child_node

    @staticmethod
    def find_all_bases(node: ast.ClassDef) -> Generator[str, None, None]:
        """Find all base classes (name) for given AST class node."""
        for base in node.bases:
            if isinstance(base, ast.Name):
                yield base.id

    @staticmethod
    def find_all_method_arguments(
        node: ast.FunctionDef,
    ) -> Generator[Tuple[str, str, set[str]], None, None]:
        """find all method arguments (including annotations)."""
        for child_node in ast.iter_child_nodes(node.args):
            if isinstance(child_node, ast.arg):
                argument_name: str = child_node.arg
                argument_type: str = ""
                names: list[str] = []

                if child_node.annotation:
                    argument_type, names = ParserTools.resolve_annotation(
                        child_node.annotation
                    )

                yield argument_name, argument_type, set(names)

    @staticmethod
    def find_all_instance_attributes(node: ast.FunctionDef):
        """Provide all instance attributes of a class."""
        if node.name == "__init__":
            for child_node in ast.iter_child_nodes(node):
                if not isinstance(child_node, ast.AnnAssign):
                    continue
                if not isinstance(child_node.target, ast.Attribute):
                    continue
                if not isinstance(child_node.target.value, ast.Name):
                    continue
                if not child_node.target.value.id == "self":
                    continue

                attribute_name: str = child_node.target.attr
                attribute_type: str = ""
                names: list[str] = []

                if child_node.annotation:
                    attribute_type, names = ParserTools.resolve_annotation(
                        child_node.annotation
                    )

                yield attribute_name, attribute_type, names

    @staticmethod
    def resolve_annotation(node: ast.AST) -> Tuple[str, list[str]]:
        """Trying to convert annotation back to code."""
        if node is None:
            return "", []

        if isinstance(node, ast.Name):
            return node.id, [node.id]

        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return node.value, [node.value]
            return repr(node.value), []

        if isinstance(node, ast.Subscript):
            value_str, value_refs = ParserTools.resolve_annotation(node.value)
            slice_node = getattr(node.slice, "value", node.slice)
            slice_str, slice_refs = ParserTools.resolve_annotation(slice_node)
            return f"{value_str}[{slice_str}]", value_refs + slice_refs

        if isinstance(node, ast.Attribute):
            base_str, base_refs = ParserTools.resolve_annotation(node.value)
            full_name = f"{base_str}.{node.attr}" if base_str else node.attr
            return full_name, base_refs + [full_name]

        try:
            text = ast.unparse(node)
        except Exception:
            text = ast.dump(node)
        return text, []

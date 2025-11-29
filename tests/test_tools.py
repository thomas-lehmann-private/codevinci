"""Test of parser tools."""

import ast

from codevinci.parser.tools import ParserTools

PACKAGE_PATH = "codevinci"


def test_find_all_classes():
    """Testing of parsing all classes."""
    parsed_classes = list(ParserTools.find_all_classes(PACKAGE_PATH))
    assert len(parsed_classes) > 0

    class_names = [node.name for file, node in parsed_classes]
    # probe tests
    assert "ClassModel" in class_names
    assert "ParserTools" in class_names


def test_find_all_classes_benchmark(benchmark):
    """Benchmark for ParserTools.find_all_classes."""
    benchmark(ParserTools.find_all_classes, PACKAGE_PATH)


def test_find_all_bases():
    """Testing of parsing all bases of a class node."""
    for _, node in ParserTools.find_all_classes(PACKAGE_PATH):
        if node.name == "ClassModel":
            bases = list(ParserTools.find_all_bases(node))
            assert len(bases) == 1
            assert "AbstractBaseModel" in bases
            break


def test_find_all_bases_benchmark(benchmark):
    """Benchmark for ParserTools.find_all_classes."""
    for _, node in ParserTools.find_all_classes(PACKAGE_PATH):
        if node.name == "ClassModel":
            benchmark(ParserTools.find_all_bases, node)
            break


def test_find_all_methods():
    """Testing of parsing all methods of a class node."""
    names = []
    for _, node in ParserTools.find_all_classes(PACKAGE_PATH):
        if node.name == "ClassModel":
            methods_nodes = list(ParserTools.find_all_methods(node))
            names = [node.name for node in methods_nodes]

    # probe tests
    assert "__init__" in names
    assert "get_name" in names


def test_find_all_methods_benchmark(benchmark):
    """Benchmark for ParserTools.find_all_methods."""
    for _, node in ParserTools.find_all_classes(PACKAGE_PATH):
        if node.name == "ClassModel":
            benchmark(ParserTools.find_all_methods, node)
            break


def test_find_all_instance_attributes():
    """Testing of parsing all instance attributes of a class node."""
    result = []
    for _, node in ParserTools.find_all_classes(PACKAGE_PATH):
        if node.name == "ClassModel":
            methods_nodes = list(ParserTools.find_all_methods(node))
            for method_node in methods_nodes:
                if method_node.name == "__init__":
                    result = list(ParserTools.find_all_instance_attributes(method_node))

    # probe tests
    assert result[1][0] == "__name"
    assert result[1][1] == "str"
    assert result[2][0] == "__methods"
    assert result[2][1] == "list[MethodModel]"


def test_find_all_instance_attributes_with_no_attributes():
    """Test for ctor where there is no instance attribute."""
    tree = ast.parse(
        """
class Demo:
    def __init__(self):
        message: str = 'hello world!'
    """
    )

    node = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)][0]
    attributes = list(ParserTools.find_all_instance_attributes(node))
    assert len(attributes) == 0


def test_find_all_instance_attributes_benchmark(benchmark):
    """Benchmark for ParserTools.find_all_instance_attributes."""
    benchmark(ParserTools.find_all_instance_attributes, PACKAGE_PATH)

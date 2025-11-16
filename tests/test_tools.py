"""Test of parser tools."""

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


def test_find_all_bases():
    """Testing of parsing all bases of a class node."""
    for _, node in ParserTools.find_all_classes(PACKAGE_PATH):
        if node.name == "ClassModel":
            bases = list(ParserTools.find_all_bases(node))
            assert len(bases) == 1
            assert "AbstractBaseModel" in bases
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

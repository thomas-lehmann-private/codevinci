""" "Test of module classes."""

from codevinci.parser import (
    ClassModel,
    ClassAttributeModel,
    DependencyModel,
    DependencyType,
    MethodModel,
    MethodType,
    MethodAccessType,
    ModelType,
    ModuleModel,
    Origin,
)

import pytest


def test_class_model_basics():
    """Test basics of class ClassModel."""
    model = ClassModel("test")
    assert model.get_name() == "test"
    assert model.get_model_type() == ModelType.CLASS
    assert model.get_origin() == Origin.PACKAGE
    assert len(model.get_methods()) == 0
    assert len(model.get_bases()) == 0
    assert not model.has_attributes()
    assert not model.has_class_attributes()
    assert not model.has_methods()
    assert str(model) == "ClassModel(test)"

    model = ClassModel("test", Origin.BUILTIN)
    assert model.get_origin() == Origin.BUILTIN


def test_class_model_with_one_methods():
    """Test of ClassModel with one method."""
    model = ClassModel("test")
    method = MethodModel("get_value")
    model.add_method(method)
    assert model.get_name() == "test"
    assert len(model.get_methods()) == 1
    assert model.has_methods()
    assert model.get_methods()[0] == method


def test_class_model_with_multiple_methods():
    """Test of ClassModel with multiple methods."""
    model = ClassModel("test")
    model.add_method(MethodModel("__init__"))
    model.add_method(MethodModel("get_value"))
    model.add_method(MethodModel("_get_value"))
    model.add_method(MethodModel("__get_value"))

    methods = model.get_methods_by_access_type(MethodAccessType.ALL)
    assert len(methods) == 4
    methods = model.get_methods_by_access_type(MethodAccessType.PUBLIC)
    assert methods[0].get_name() == "__init__"
    assert methods[1].get_name() == "get_value"
    assert len(methods) == 2
    methods = model.get_methods_by_access_type(MethodAccessType.PROTECTED)
    assert len(methods) == 1
    assert methods[0].get_name() == "_get_value"
    methods = model.get_methods_by_access_type(MethodAccessType.PRIVATE)
    assert len(methods) == 1
    assert methods[0].get_name() == "__get_value"


def test_class_model_with_class_attributes():
    """Testing class attributes."""
    model = ClassModel("ModelType")
    model.add_class_attribute(ClassAttributeModel("MODULE"))
    model.add_class_attribute(ClassAttributeModel("MODULE"))
    model.add_class_attribute(ClassAttributeModel("CLASS"))
    assert model.has_class_attributes()
    class_attributes = model.get_class_attributes()
    assert len(class_attributes) == 2
    assert class_attributes[0].get_name() == "MODULE"
    assert class_attributes[1].get_name() == "CLASS"


def test_class_attributes_model():
    """Testing class ClassAttributesModel."""
    model = ClassAttributeModel("MODULE")
    assert model.get_name() == "MODULE"
    assert model.get_model_type() == ModelType.CLASS_ATTRIBUTE
    assert model.get_origin() == Origin.CLASS
    assert model == ClassAttributeModel("MODULE")

    with pytest.raises(NotImplementedError):
        model == ClassModel("ModelType")  # pyright: ignore[reportUnusedExpression]


def test_method_model_basics():
    """Test of MethodModel."""
    model = MethodModel("test")
    assert model.get_name() == "test"
    assert model.get_model_type() == ModelType.METHOD
    assert model.get_origin() == Origin.CLASS
    assert model.get_method_type() == MethodType.NORMAL
    assert str(model) == "MethodModel(test)"

    model.set_method_type(MethodType.STATIC)
    assert model.get_method_type() == MethodType.STATIC
    model.set_method_type(MethodType.ABSTRACT)
    assert model.get_method_type() == MethodType.ABSTRACT


@pytest.mark.parametrize(
    "method_name,expected_access_type",
    [
        ("__init__", MethodAccessType.PUBLIC),
        ("is_abstract_method", MethodAccessType.PUBLIC),
        ("__find_class_model_by_name", MethodAccessType.PRIVATE),
        ("_calculate_something", MethodAccessType.PROTECTED),
    ],
)
def test_method_access_type(method_name, expected_access_type):
    """Testing method access type"""
    methodModel = MethodModel(method_name)
    assert methodModel.get_access_type() == expected_access_type


def test_module_model_default():
    """Testing basics of class ModuleModel."""
    model = ModuleModel("pyclass2graph/parser/parser.py")
    assert model.get_name() == "parser"
    assert model.get_model_type() == ModelType.MODULE
    assert model.get_origin() == Origin.PACKAGE
    assert str(model) == "ModuleModel(parser)"


def test_dependency_model():
    """Testing of DependencyModel class."""
    classModel1 = ClassModel("source")
    classModel2 = ClassModel("destination")
    dependency = DependencyModel(classModel1, classModel2, DependencyType.BASE_CLASS)
    assert dependency.get_model_type() == ModelType.DEPENDENCY
    assert dependency.get_dependency_type() == DependencyType.BASE_CLASS
    assert dependency.get_origin() == Origin.PACKAGE
    assert dependency.get_source_model() == classModel1
    assert dependency.get_destination_model() == classModel2
    assert (
        str(dependency)
        == "DependencyModel(ClassModel(source), ClassModel(destination),DependencyType.BASE_CLASS)"
    )

    with pytest.raises(NotImplementedError):
        dependency.get_name()

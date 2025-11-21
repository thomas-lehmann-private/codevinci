"""Module generator."""

from abc import ABC, abstractmethod
from enum import Enum
from logging import getLogger, Logger
from typing import Any

from codevinci.parser import ClassModel, DependencyType, MethodType, ModuleModel

import graphviz


class GeneratorOutputFormat(Enum):
    """Defines available generator output types."""

    SVG = 1
    PNG = 2
    SOURCE = 3


class GeneratorOptions:
    """Options for a concrete generator."""

    def __init__(self, output_format: GeneratorOutputFormat, output_path: str):
        """Initialize generator options."""
        self.__output_format = output_format
        self.__output_path = output_path

    def get_output_format(self) -> GeneratorOutputFormat:
        """Get defined output type."""
        return self.__output_format

    def get_output_path(self) -> str:
        """Get defined output path."""
        return self.__output_path


class AbstractClassGenerator(ABC):
    """Base class for class generators."""

    @abstractmethod
    def generate(self, moduleModels: list[ModuleModel]) -> Any:
        """Main entry point for processing modules."""
        ...

    @abstractmethod
    def generate_module(
        self, parent: graphviz.graphs.Digraph, moduleModel: ModuleModel
    ) -> None:
        """Generate diagram part for a module."""
        ...

    @abstractmethod
    def generate_class(
        self, parent: graphviz.graphs.Digraph, classModel: ClassModel
    ) -> None:
        """Generate diagram part for a class."""
        ...

    @abstractmethod
    def generate_dependencies(self, parent: graphviz.graphs.Digraph) -> None:
        """Generate diagram part for a dependency."""
        ...


class GraphvizClassGenerator(AbstractClassGenerator):
    """Diagram generator using the Graphviz library."""

    def __init__(self, options: GeneratorOptions):
        """Initialize processor."""
        self.__logger: Logger = getLogger(__name__)
        self.__options = options
        self.__dependencies = []

    def generate(self, moduleModels: list[ModuleModel]) -> Any:
        """Main entry point for processing modules."""
        dot = graphviz.Digraph("classes", comment="classes and relationships")

        for moduleModel in moduleModels:
            self.__logger.info(f"processing module '{moduleModel.get_name()}'")
            self.generate_module(dot, moduleModel)

        self.generate_dependencies(dot)

        match self.__options.get_output_format():
            case GeneratorOutputFormat.SVG:
                return dot.pipe(format="svg")
            case GeneratorOutputFormat.PNG:
                return dot.pipe(format="png")
            case GeneratorOutputFormat.SOURCE:
                return dot.source

    def generate_module(
        self, parent: graphviz.graphs.Digraph, moduleModel: ModuleModel
    ) -> None:
        """Generate diagram part for a module."""
        with parent.subgraph(name=f"cluster_{moduleModel.get_name()}") as module:  # type: ignore[reportOptionalContextManager]
            module.attr(label=moduleModel.get_name())
            for classModel in moduleModel.get_classes():
                self.__logger.info(f"processing class '{classModel.get_name()}'")
                self.generate_class(module, classModel)

    def generate_class(
        self, parent: graphviz.graphs.Digraph, classModel: ClassModel
    ) -> None:
        """Generate diagram part for a class."""
        method_description = self.__get_method_description(classModel)
        description = '<<table border="0" cellborder="1" cellspacing="0">'
        if classModel.is_abstract():
            description += (
                "<tr><td><b>"
                + classModel.get_name()
                + "<br/><i>Abstract Base Class</i></b></td></tr>"
            )
        elif classModel.is_enum():
            description += (
                "<tr><td><b>"
                + classModel.get_name()
                + "<br/><i>Enum Class</i></b></td></tr>"
            )
        else:
            description += "<tr><td><b>" + classModel.get_name() + "</b></td></tr>"

        attributes_description = self.__get_attributes_description(classModel)
        if attributes_description:
            description += "<tr><td>" + attributes_description + "</td></tr>"
        if method_description:
            description += "<tr><td>" + method_description + "</td></tr>"
        description += "</table>>"
        parent.node(classModel.get_name(), description, shape="plain")
        # remember base class dependencies
        self.__dependencies.extend(classModel.get_bases())

    def generate_dependencies(self, parent: graphviz.graphs.Digraph):
        """Generate diagram part for dependencies."""
        for dependency in self.__dependencies:
            if dependency.get_dependency_type() == DependencyType.BASE_CLASS:
                if dependency.get_destination_model().get_name() not in ["Enum", "ABC"]:
                    parent.edge(
                        dependency.get_source_model().get_name(),
                        dependency.get_destination_model().get_name(),
                        "base",
                    )
            elif (
                dependency.get_dependency_type() == DependencyType.METHOD_ARGUMENT_TYPE
            ):
                class_name = dependency.get_source_model().get_owner().get_name()
                method_name = dependency.get_source_model().get_name()
                parent.edge(
                    f"{class_name}:{method_name}:e",
                    dependency.get_destination_model().get_name(),
                    "depends",
                )
            elif (
                dependency.get_dependency_type()
                == DependencyType.INSTANCE_ATTRIBUTE_TYPE
            ):
                class_name = dependency.get_source_model().get_owner().get_name()
                attribute_name = dependency.get_source_model().get_name()
                parent.edge(
                    f"{class_name}:{attribute_name}:e",
                    dependency.get_destination_model().get_name(),
                    "depends",
                )
            else:
                parent.edge(
                    dependency.get_source_model().get_name(),
                    dependency.get_destination_model().get_name(),
                    "depends",
                )

    def __get_attributes_description(self, classModel: ClassModel) -> str:
        """Generate attrinutes for classes in diagramm."""
        instance_attributes_description = ""
        if classModel.has_attributes():
            instance_attributes_description = (
                '<table border="0" cellborder="0" cellspacing="0">'
            )
            for attributeModel in classModel.get_attributes():
                port = attributeModel.get_name()
                instance_attributes_description += (
                    f"""<tr><td port="{port}" align="left">"""
                )
                instance_attributes_description += attributeModel.get_name()
                if attributeModel.get_attribute_type():
                    instance_attributes_description += (
                        f" : {attributeModel.get_attribute_type()}"
                    )
                instance_attributes_description += "</td></tr>"
                # provide dependencies
                self.__dependencies.extend(attributeModel.get_dependencies())

            instance_attributes_description += "</table>"

        return instance_attributes_description

    def __get_method_description(self, classModel: ClassModel) -> str:
        """Generate method description when given class has methods."""
        method_description = ""
        if classModel.has_methods():

            method_description = '<table border="0" cellborder="0" cellspacing="0">'
            for methodModel in classModel.get_methods():
                method_argument_description = ""
                for argument in methodModel.get_arguments():
                    if len(method_argument_description) > 0:
                        method_argument_description += ", "
                    method_argument_description += argument.get_name()
                    if len(argument.get_argument_type()):
                        method_argument_description += " : "
                        method_argument_description += argument.get_argument_type()

                port = methodModel.get_name()
                method_description += f"""<tr><td port="{port}" align="left">"""
                match methodModel.get_method_type():
                    case MethodType.NORMAL:
                        method_description += methodModel.get_name()
                    case MethodType.ABSTRACT:
                        method_description += "<i>" + methodModel.get_name() + "</i>"
                    case MethodType.STATIC:
                        method_description += "<u>" + methodModel.get_name() + "</u>"
                method_description += "("
                method_description += method_argument_description
                method_description += ")"

                if methodModel.get_return_type():
                    method_description += " : " + methodModel.get_return_type()

                method_description += "</td></tr>"

                self.__dependencies.extend(methodModel.get_dependencies())

            method_description += "</table>"
        return method_description

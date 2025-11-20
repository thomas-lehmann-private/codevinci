"""Module model."""

from abc import ABC, abstractmethod
from enum import Enum
from logging import getLogger, Logger
import os


class ModelType(Enum):
    """Types of models."""

    MODULE = 1
    CLASS = 2
    METHOD = 3
    METHOD_ARGUMENT = 4
    DEPENDENCY = 5
    INSTANCE_ATTRIBUTE = 6


class DependencyType(Enum):
    """Types of dependencies."""

    BASE = 1
    METHOD_ARGUMENT = 2
    INSTANCE_ATTRIBUTE = 3


class Origin(Enum):
    """Where it does come from."""

    PACKAGE = 1
    BUILTIN = 2
    CLASS = 3
    METHOD = 4


class AbstractBaseModel(ABC):
    """Base class for models."""

    @abstractmethod
    def get_name(self) -> str:
        """Name of what the model does contain."""
        ...

    @abstractmethod
    def get_model_type(self) -> ModelType:
        """Get type of model."""
        ...

    @abstractmethod
    def get_origin(self) -> Origin:
        """Get location of what the model does have as information."""
        ...


class ClassModel(AbstractBaseModel):
    """Model for a class."""

    def __init__(self, name: str, origin: Origin = Origin.PACKAGE) -> None:
        """Initialize ClassModel instance."""
        self.__logger: Logger = getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        self.__name: str = name
        self.__methods: list[MethodModel] = []
        self.__bases: list[DependencyModel] = []
        self.__origin: Origin = origin
        self.__attributes: list[InstanceAttributeModel] = []

    def __repr__(self):
        """String representation of ClassModel instance."""
        return f"ClassModel({self.__name})"

    def get_model_type(self) -> ModelType:
        """Get type of model."""
        return ModelType.CLASS

    def get_name(self) -> str:
        """Name of the class."""
        return self.__name

    def get_origin(self) -> Origin:
        """Get location of the class."""
        return self.__origin

    def add_method(self, method: "MethodModel") -> None:
        """Add a method."""
        method.set_owner(self)
        self.__methods.append(method)
        self.__logger.info(f"{method} added to {self}")

    def has_methods(self) -> bool:
        """Check whether class has methods."""
        return len(self.__methods) > 0

    def get_methods(self) -> list["MethodModel"]:
        """Get list of methods."""
        return self.__methods

    def add_base(self, base: "DependencyModel") -> None:
        """Add a base class dependency."""
        self.__bases.append(base)
        self.__logger.info(
            f"base {base.get_destination_model()} added to {self} as dependency"
        )

    def get_bases(self) -> list["DependencyModel"]:
        """Provide list of base class dependencies."""
        return self.__bases

    def add_attribute(self, attribute: "InstanceAttributeModel") -> None:
        """Add instance attribute to class."""
        attribute.set_owner(self)
        self.__attributes.append(attribute)
        self.__logger.info(f"{attribute} added to {self}")

    def get_attributes(self) -> list["InstanceAttributeModel"]:
        """Provide list of instance attributes."""
        return self.__attributes

    def has_attributes(self) -> bool:
        """Check whether there are instance attributes."""
        return len(self.__attributes) > 0

    def is_abstract(self):
        """Check whether given class is derived from 'ABC'."""
        # TODO: also check whether there is at least one method
        #       that has annotation @abstractmethod
        for base in self.__bases:
            if base.get_destination_model().get_name() == "ABC":
                return True
        return False

    def is_enum(self):
        """Check whether given class is derived from 'Enum'."""
        for base in self.__bases:
            if base.get_destination_model().get_name() == "Enum":
                return True
        return False


class ModuleModel(AbstractBaseModel):
    """Represent a module."""

    def __init__(self, path: str) -> None:
        """Initialize model for module."""
        self.__logger: Logger = getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        self.__path: str = path
        self.__name: str = os.path.splitext(os.path.basename(path))[0]
        self.__classModels: list[ClassModel] = []

    def __repr__(self):
        """String representation of this class (simplified)."""
        return f"ModuleModel({self.__name})"

    def get_model_type(self) -> ModelType:
        """Get type of model."""
        return ModelType.MODULE

    def get_name(self) -> str:
        """Name of the module."""
        return self.__name

    def get_origin(self) -> Origin:
        """Get location of the module."""
        return Origin.PACKAGE

    def add_class(self, classModel: ClassModel) -> None:
        """Add a class to the module."""
        self.__classModels.append(classModel)
        self.__logger.info(f"{classModel} added to {self}")

    def get_classes(self) -> list[ClassModel]:
        """Get list of classes."""
        return self.__classModels

    def __eq__(self, other) -> bool:
        """Compare to modules to be equal."""
        if not isinstance(other, ModuleModel):
            raise NotImplementedError
        return self.__path == other.__path

    def __hash__(self) -> int:
        """Unique hash for current module instance."""
        return hash(self.__path)


class MethodArgumentModel(AbstractBaseModel):
    """Model for a method argument."""

    def __init__(self, name: str, argument_type: str) -> None:
        """Initialize model for an argument."""
        self.__name: str = name
        self.__argument_type = argument_type

    def get_model_type(self) -> ModelType:
        """Get type of model."""
        return ModelType.METHOD_ARGUMENT

    def get_name(self) -> str:
        """Name of the method."""
        return self.__name

    def get_argument_type(self) -> str:
        """Get type of argument."""
        return self.__argument_type

    def get_origin(self) -> Origin:
        """Get location of the methods."""
        return Origin.METHOD


class MethodModel(AbstractBaseModel):
    """Model for a method."""

    def __init__(self, name: str) -> None:
        """Initialize model for a method.

        Args:
            name: name of the method.
        """
        self.__name: str = name
        self.__arguments: list[MethodArgumentModel] = []
        self.__dependencies: list[DependencyModel] = []
        self.__owner: ClassModel | None = None
        self.__return_type: str = ""

    def __repr__(self) -> str:
        """String representation of the model (simplified)."""
        return f"MethodModel({self.__name})"

    def get_model_type(self) -> ModelType:
        """Get type of model.

        Returns:
            Type of the model (here: a method)
        """
        return ModelType.METHOD

    def get_name(self) -> str:
        """Name of the method."""
        return self.__name

    def get_origin(self) -> Origin:
        """Get location of the methods."""
        return Origin.CLASS

    def add_argument(self, argument: MethodArgumentModel) -> None:
        """Add one argument to method."""
        self.__arguments.append(argument)

    def get_arguments(self) -> list[MethodArgumentModel]:
        """Provide list of method arguments."""
        return self.__arguments

    def add_dependency(self, dependency: "DependencyModel"):
        """Adding a dependency."""
        self.__dependencies.append(dependency)

    def get_dependencies(self):
        """Get dependencies of method to another class in the packages."""
        return self.__dependencies

    def set_owner(self, owner: ClassModel) -> None:
        """Set owner of this method"""
        self.__owner = owner

    def get_owner(self) -> ClassModel | None:
        """Provide owner of this method."""
        return self.__owner

    def set_return_type(self, return_type: str) -> None:
        """Change return type."""
        self.__return_type = return_type

    def get_return_type(self) -> str:
        """Provide return type."""
        return self.__return_type


class InstanceAttributeModel(AbstractBaseModel):
    """Model for an instance attribute."""

    def __init__(self, name: str, attribute_type: str) -> None:
        """Initialize model for an argument."""
        self.__logger: Logger = getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        self.__name: str = name
        self.__attribute_type = attribute_type
        self.__dependencies: list[DependencyModel] = []
        self.__owner: ClassModel | None = None

    def __repr__(self) -> str:
        """String representation of this class (simplifief)."""
        return f"InstanceAttributeModel({self.__name})"

    def get_model_type(self) -> ModelType:
        """Get type of model."""
        return ModelType.INSTANCE_ATTRIBUTE

    def get_name(self) -> str:
        """Name of the instance attribute."""
        return self.__name

    def get_attribute_type(self) -> str:
        """Get type of instance attribute."""
        return self.__attribute_type

    def get_origin(self) -> Origin:
        """Get location of the instance attribute."""
        return Origin.CLASS

    def set_owner(self, owner: ClassModel) -> None:
        """Set owner of this method"""
        self.__owner = owner

    def get_owner(self) -> ClassModel | None:
        """Provide owner of this method."""
        return self.__owner

    def add_dependency(self, dependency: "DependencyModel") -> None:
        """Adding a dependency."""
        if dependency.get_source_model() == self:
            self.__dependencies.append(dependency)
            self.__logger.info(f"{dependency} added to {self} of {self.__owner}")

    def get_dependencies(self) -> list["DependencyModel"]:
        """Get dependencies of instance attribute to another class in the packages."""
        return self.__dependencies


class DependencyModel(AbstractBaseModel):
    """Defines dependency of a model to a class."""

    def __init__(
        self,
        sourceModel: AbstractBaseModel,
        destinationModel: ClassModel,
        dependencyType: DependencyType,
    ) -> None:
        """Initialize model for a dependency."""
        self.__sourceModel: AbstractBaseModel = sourceModel
        self.__destinationModel: ClassModel = destinationModel
        self.__dependencyType = dependencyType

    def get_model_type(self) -> ModelType:
        """Get type of model."""
        return ModelType.DEPENDENCY

    def get_name(self):
        """Dependencies do not have a name."""
        raise NotImplementedError

    def get_origin(self) -> Origin:
        """Get location of the dependency (source)."""
        return Origin.PACKAGE

    def get_source_model(self) -> AbstractBaseModel:
        """Provide source of dependency."""
        return self.__sourceModel

    def get_destination_model(self) -> ClassModel:
        """Provide destination of dependency."""
        return self.__destinationModel

    def get_dependency_type(self) -> DependencyType:
        """Provide destination of dependency."""
        return self.__dependencyType

    def __repr__(self):
        """String representation of the instance."""
        return f"DependencyModel({self.__sourceModel}, {self.__destinationModel},{self.__dependencyType})"

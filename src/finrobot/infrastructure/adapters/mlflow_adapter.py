"""Savers, loaders, and registers for model registries."""
# mypy: disable-error-code=override

# %% IMPORTS

import abc
import typing as T
from typing import Any, Dict

import mlflow
import mlflow.entities
import mlflow.entities.model_registry
import mlflow.models.model
import pandas as pd
import pydantic as pdt
from finrobot.models import schemas

# %% TYPES

# Results of model registry operations
Info: T.TypeAlias = mlflow.models.model.ModelInfo
Alias: T.TypeAlias = mlflow.entities.model_registry.ModelVersion
Version: T.TypeAlias = mlflow.entities.model_registry.ModelVersion

# %% HELPERS


def uri_for_model_alias(name: str, alias: str) -> str:
    """Create a model URI from a model name and an alias.

    Args:
        name (str): name of the mlflow registered model.
        alias (str): alias of the registered model.

    Returns:
        str: model URI as "models:/name@alias".
    """
    return f"models:/{name}@{alias}"


def uri_for_model_version(name: str, version: str) -> str:
    """Create a model URI from a model name and a version.

    Args:
        name (str): name of the mlflow registered model.
        version (int): version of the registered model.

    Returns:
        str: model URI as "models:/name/version."
    """
    return f"models:/{name}/{version}"


def uri_for_model_alias_or_version(name: str, alias_or_version: str | int) -> str:
    """Create a model URi from a model name and an alias or version.

    Args:
        name (str): name of the mlflow registered model.
        alias_or_version (str | int): alias or version of the registered model.

    Returns:
        str: model URI as "models:/name@alias" or "models:/name/version" based on input.
    """
    if isinstance(alias_or_version, int):
        return uri_for_model_version(name=name, version=str(alias_or_version))
    else:
        return uri_for_model_alias(name=name, alias=alias_or_version)


# %% LOADERS


class Loader(abc.ABC, pdt.BaseModel, strict=True, frozen=True, extra="forbid"):
    """Base class for loading models from registry.

    Separate model definition from deserialization.
    e.g., to switch between deserialization flavors.
    """

    KIND: str

    class Adapter(abc.ABC):
        """Adapt any model for the project inference."""

        @abc.abstractmethod
        def load_context(self, model_config: Dict[str, Any]) -> None:
            """
            Load the model from the specified artifacts directory.
            """

        @abc.abstractmethod
        def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
            """Generate predictions with the internal model for the given inputs.

            Args:
                inputs (schemas.Inputs): validated inputs for the project model.

            Returns:
                schemas.Outputs: validated outputs of the project model.
            """

    @abc.abstractmethod
    def load(self, uri: str) -> "Loader.Adapter":
        """Load a model from the model registry.

        Args:
            uri (str): URI of a model to load.

        Returns:
            Loader.Adapter: model loaded.
        """


class CustomLoader(Loader):
    """Loader for custom models using the Mlflow PyFunc module.

    https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html
    """

    KIND: T.Literal["CustomLoader"] = "CustomLoader"

    class Adapter(Loader.Adapter):
        """Adapt a custom model for the project inference."""

        def __init__(self, model: mlflow.pyfunc.PyFuncModel) -> None:  # type: ignore[name-defined]
            """Initialize the adapter from an mlflow pyfunc model.

            Args:
                model (mlflow.pyfunc.PyFuncModel): mlflow pyfunc model.
            """
            self.model = model

        def load_context(self, model_config: Dict[str, Any]) -> None:
            """
            Load the model from the specified artifacts directory.
            """
            self.model.load_context(model_config)

        def predict(self, inputs: schemas.Inputs) -> schemas.Outputs:
            # model validation is already done in predict
            prediction = self.model.predict(data=inputs)

            # Return the outputs schema
            outputs = schemas.Outputs(
                pd.DataFrame(
                    {
                        "response": [prediction],
                        "metadata": [{"timestamp": "2025-01-15T12:00:00Z", "model_version": "v1.0.0"}],
                    }
                )
            )
            return outputs

    def load(self, uri: str) -> "CustomLoader.Adapter":
        model = mlflow.pyfunc.load_model(model_uri=uri)
        adapter = CustomLoader.Adapter(model=model)
        return adapter


LoaderKind = CustomLoader

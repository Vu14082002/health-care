from typing import Callable, Any, List, _UnionGenericAlias
from starlette.routing import Route
from src.core import logger
from pydantic import BaseModel
from src.core.security import Authorization, JsonWebToken

import inspect
import yaml

# _UnionGenericAlias = dict


class RouteSwagger(Route):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        methods: List[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        tags: List[str] = ["Default"]
    ) -> None:
        super().__init__(
            path,
            endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
        self.tags = tags
        # Generate swagger documentation for the endpoint.
        for name, func in endpoint.__dict__.items():
            # swagger_generate is a swagger_generate function that is used to generate swagger documentation
            if name in ["get", "post", "put", "delete"]:
                _signature = inspect.signature(func)
                _summary = func.__doc__
                func.__doc__ = self.swagger_generate(_signature, _summary)

    def swagger_generate(
        self, signature: inspect.Signature, summary: str = "Document API"
    ):
        """
        Generate Swagger documentation for a request. This is a helper method to generate a Swagger document based on information provided by the client.

        @param signature - The signature of the request. Must be annotated with
        @param summary - A description of the request. Defaults to " Document API "

        @return A dictionary of the form { " doc " : {
        """
        _inputs = signature.parameters.values()
        _inputs_dict = {_input.name: _input.annotation for _input in _inputs}
        _docs = {"summary": summary, "tags": self.tags, "responses": []}
        _response_type = signature.return_annotation

        # This function is used to generate the documentation for the mapping.
        for key, item in _inputs_dict.items():

            # Add a security object to the docs.
            if isinstance(item, type) and issubclass(item, Authorization):
                auth_obj = item()
                _docs["security"] = [{auth_obj.name: []}]

            # This is a dictionary of model_fields and parameters.
            if isinstance(item, type) and issubclass(item, BaseModel):
                # this is the form data for the form data
                if key == "form_data":
                    _docs["requestBody"] = {
                        "content": {
                            "multipart/form-data": {"schema": item.model_json_schema()}
                        }
                    }

                # This is the key query_params.
                if key == "query_params":
                    _parameters = []
                    # Add a parameter to the query.
                    for name, field in item.model_fields.items():
                        _type = field.annotation
                        # A type is a _UnionGenericAlias.
                        if isinstance(_type, _UnionGenericAlias):
                            _type = _type.__args__[0]
                        _parameters.append(
                            {
                                "name": name,
                                "in": "query",
                                "required": field.is_required(),
                                "description": field.description,
                                "example": field.examples,
                                "schema": {
                                    "type": self.mapping_type.get(_type, "string"),
                                },
                            }
                        )
                    _docs["parameters"] = _parameters

                # path_params is the key of the path_params key.
                if key == "path_params":
                    _parameters = []
                    # Add the parameters to the parameters list.
                    for name, field in item.model_fields.items():
                        _type = field.annotation
                        # A type is a _UnionGenericAlias.
                        if isinstance(_type, _UnionGenericAlias):
                            _type = _type.__args__[0]
                        _parameters.append(
                            {
                                "name": name,
                                "in": "path",
                                "required": self.mapping_type[field.is_required()],
                                "description": field.description,
                                "example": field.examples,
                                "schema": {
                                    "type": self.mapping_type.get(_type, "string"),
                                },
                            }
                        )
                    _docs["parameters"] = _parameters

        # Response type to be sent to the server
        if isinstance(_response_type, type) and issubclass(_response_type, BaseModel):
            _docs["responses"] = {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {"schema": _response_type.model_json_schema()}
                    },
                }
            }

        return yaml.dump(_docs)

    @property
    def mapping_type(self):
        """
        Returns the type of the data. This is used to determine how values are converted to the database's column types.


        @return A dictionary mapping column types to their data types ( strings ). The keys of the dictionary are the column names the values are the column types
        """
        return {
            str: "string",
            int: "integer",
            True: "true",
            False: "false",
            float: "float",
            bool: "boolean",
        }

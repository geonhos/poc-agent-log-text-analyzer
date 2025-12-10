"""
Common data models
"""

from .api_spec import (
    APIEndpoint,
    APISpec,
    HTTPMethod,
    Parameter,
    ParameterLocation,
    ParameterSchema,
    RequestBody,
    Response,
)
from .document import Document, DocumentCollection

__all__ = [
    # API Spec models
    "APISpec",
    "APIEndpoint",
    "HTTPMethod",
    "Parameter",
    "ParameterLocation",
    "ParameterSchema",
    "RequestBody",
    "Response",
    # Document models
    "Document",
    "DocumentCollection",
]

"""
Created on 2023-11-19

@author: wf
"""
from fastapi.responses import JSONResponse
import orjson
from typing import Any

class ORJSONResponse(JSONResponse):
    """
    A FastAPI response class that uses orjson for JSON serialization.
    """

    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        """
        Override the render method to use orjson for serialization.
        """
        return orjson.dumps(content)
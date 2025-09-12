import json
from typing import Self

from fastapi import Response


class JsonResponseBuilder:
    _MEDIA_TYPE = "application/json"

    def __init__(self) -> None:
        self._json: str | None = None
        self._status: int = 0

    def with_json(self, json_str: str) -> Self:
        self._json = json_str
        return self

    def with_dict(self, json_dict: dict) -> Self:
        self._json = json.dumps(json_dict)
        return self

    def with_status(self, status: int) -> Self:
        self._status = status
        return self

    def respond(self) -> Response:
        return Response(
            content=self._json, media_type=JsonResponseBuilder._MEDIA_TYPE, status_code=self._status
        )

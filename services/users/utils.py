from fastapi import FastAPI


def api_setup():
    """
    Customizes OpenAPI generation (removes default 422 boilerplate from OpenAPI docs).
    """
    global _openapi
    _openapi = FastAPI.openapi

    def openapi(self: FastAPI):
        _openapi(self)
        for path_item in self.openapi_schema.get("paths", {}).values():
            for operation in path_item.values():
                responses = operation.get("responses", {})
                if "422" in responses:
                    del responses["422"]
        return self.openapi_schema

    FastAPI.openapi = openapi

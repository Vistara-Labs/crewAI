import json
from typing import Type
import registry

from crewai.tools import BaseTool
from pydantic import BaseModel

# Convert a Pydantic model dump JSON to a Model object
def create_model_from_json_schema(schema_name, schema_json) -> Type[BaseModel]:
  type_mapping = {
      "string": str,
      "integer": int,
      "number": float,
      "boolean": bool, 
  }

  field_definitions = {}
  for field_name, field_schema in schema_json["properties"].items():
    field_type = type_mapping[field_schema["type"]]
    field_definitions[field_name] = (field_type, Field(description=field_schema.get("description")))

  return create_model(schema_json["title"], **field_definitions)

# Create a virtual tool to proxy all calls to the hosted tool
def create_virtual_tool(remote_tool: registry.RemoteTool):
    class VirtualTool(BaseTool):
        __qualname__ = remote_tool.class_name
        __name__ = remote_tool.class_name

        name: str = remote_tool.name
        description: str = remote_tool.description
        args_schema: Type[BaseModel] = create_model_from_json_schema(remote_tool.model_dict)

        def _run(self, **kwargs):
            return registry.execute_tool(remote_tool.class_name, kwargs)
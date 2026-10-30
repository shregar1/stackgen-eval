"""ToolCall model definition."""

from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ToolCall(BaseModel):
    """Represents a single tool invocation within an agent execution trace."""
    model_config = ConfigDict(extra="ignore")

    tool: str = Field(description="Name of the invoked tool.")
    request: Any = Field(default_factory=dict, description="Arguments/payload passed to the tool.")
    result: Optional[Any] = Field(default=None, description="System payload returned by the tool.")
    error: Optional[Any] = Field(default=None, description="Error message or exception if the tool failed.")

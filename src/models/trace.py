"""Trace model definition."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.models.tool_call import ToolCall


class Trace(BaseModel):
    """Complete machine-readable execution trace for an AI agent interaction."""
    model_config = ConfigDict(extra="ignore")

    trace_id: int = Field(description="Unique numeric identifier for the trace.")
    title: Optional[str] = Field(default="", description="Descriptive title of the scenario.")
    request: str = Field(description="User prompt / request provided to the agent.")
    available_tools: List[str] = Field(
        default_factory=list,
        description="List of tool definitions available to the agent during execution."
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Sequential list of tool calls made by the agent."
    )
    reply: str = Field(description="The final message presented to the user.")

"""Adapter converting Berkeley Function Calling Leaderboard (BFCL) benchmark entries to Trace models."""

import re
import json
import urllib.request
from typing import Any, Dict, List, Optional
from src.models.trace import Trace
from src.models.tool_call import ToolCall


class BFCLDatasetAdapter:
    """
    Adapter Pattern implementation transforming raw UC Berkeley Function Calling Leaderboard (BFCL)
    benchmark entries (from gorilla-llm/Berkeley-Function-Calling-Leaderboard) into standardized
    StackGen Trace models for evaluation.
    """

    DEFAULT_BFCL_URL: str = (
        "https://huggingface.co/datasets/gorilla-llm/Berkeley-Function-Calling-Leaderboard/raw/main/BFCL_v3_exec_simple.json"
    )

    @classmethod
    def parse_entry(cls, raw_entry: Dict[str, Any], trace_id: int) -> Trace:
        """Parse a single BFCL JSON dictionary into a Trace."""
        # 1. Extract request from multi-turn or nested question structure
        question_text = ""
        question_data = raw_entry.get("question", [])
        if isinstance(question_data, list) and question_data:
            first_turn = question_data[0]
            if isinstance(first_turn, list) and first_turn:
                question_text = first_turn[0].get("content", "")
            elif isinstance(first_turn, dict):
                question_text = first_turn.get("content", "")
        elif isinstance(question_data, str):
            question_text = question_data

        # 2. Extract available tool names
        available_tools: List[str] = []
        for fn in raw_entry.get("function", []):
            if isinstance(fn, dict) and "name" in fn:
                available_tools.append(fn["name"])

        # 3. Extract tool calls from ground truth or execution result
        tool_calls: List[ToolCall] = []
        ground_truth = raw_entry.get("ground_truth", [])
        if isinstance(ground_truth, list):
            for gt_str in ground_truth:
                if isinstance(gt_str, str):
                    # Match func_name(arg1=val1, arg2=val2)
                    match = re.match(r"^([a-zA-Z0-9_]+)\((.*)\)$", gt_str.strip())
                    if match:
                        tool_name = match.group(1)
                        raw_args = match.group(2)
                        tool_calls.append(
                            ToolCall(
                                tool=tool_name,
                                request={"raw_arguments": raw_args},
                                result={"status": "success", "executed_call": gt_str}
                            )
                        )
                    else:
                        tool_calls.append(
                            ToolCall(
                                tool=available_tools[0] if available_tools else "generic_tool",
                                request={"query": gt_str},
                                result={"status": "success"}
                            )
                        )

        # 4. Generate synthesized reply from tool execution
        reply_summary = (
            f"Successfully executed {tool_calls[0].tool} for the request."
            if tool_calls else "Task completed."
        )

        return Trace(
            trace_id=trace_id,
            title=f"BFCL-{raw_entry.get('id', trace_id)}",
            request=question_text,
            available_tools=available_tools,
            tool_calls=tool_calls,
            reply=reply_summary
        )

    @classmethod
    def load_from_url(cls, url: Optional[str] = None, max_entries: int = 15) -> List[Trace]:
        """Fetch and adapt live BFCL benchmark entries from the web."""
        target_url = url or cls.DEFAULT_BFCL_URL
        req = urllib.request.Request(target_url, headers={"User-Agent": "StackGen-Evaluator/1.0"})
        traces: List[Trace] = []

        with urllib.request.urlopen(req, timeout=15) as response:
            count = 0
            for line_bytes in response:
                if count >= max_entries:
                    break
                line_str = line_bytes.decode("utf-8").strip()
                if not line_str:
                    continue
                try:
                    raw_entry = json.loads(line_str)
                    count += 1
                    trace = cls.parse_entry(raw_entry, trace_id=100 + count)
                    traces.append(trace)
                except Exception:
                    continue

        return traces

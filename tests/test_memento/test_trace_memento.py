"""Unit tests for the Memento Pattern (TraceMemento, TraceOriginator, TraceCaretaker)."""

import pytest
from src.core.builder import TraceBuilder
from src.memento.trace_memento import TraceMemento
from src.memento.trace_originator import TraceOriginator
from src.memento.trace_caretaker import TraceCaretaker
from src.pipeline import EvaluationPipeline
from src.models.eval_verdict import EvalVerdict


class TestTraceMemento:
    """Class-based test suite verifying memento state capture, caretaker management, and counterfactual restoration."""

    def test_create_and_inspect_memento(self):
        trace = (
            TraceBuilder(1)
            .with_request("What is blocking the release?")
            .with_tool_call("linear_search", result=[{"id": "ENG-41"}])
            .with_reply("ENG-41 is blocking.")
            .build()
        )

        originator = TraceOriginator(trace)
        memento = originator.create_memento(description="initial_state")

        assert memento.trace_id == 1
        assert memento.user_request == "What is blocking the release?"
        assert memento.final_reply == "ENG-41 is blocking."
        assert len(memento.tool_calls) == 1
        assert memento.description == "initial_state"
        assert memento.created_at > 0.0

    def test_restore_from_memento_after_mutation(self):
        trace = (
            TraceBuilder(5)
            .with_request("Send release announcement to team")
            .with_tool_call("slack_send", request={"channel": "#engineering", "text": "Shipped!"}, result={"ok": True})
            .with_reply("Message sent.")
            .build()
        )

        originator = TraceOriginator(trace)
        memento = originator.create_memento(description="unconfirmed_danger_state")

        # Mutate to counterfactual state
        originator.mutate_final_reply("I have drafted the message and await your confirmation.")
        mutated_trace = originator.get_trace()
        assert mutated_trace.reply == "I have drafted the message and await your confirmation."

        # Restore from memento
        originator.restore(memento)
        restored_trace = originator.get_trace()
        assert restored_trace.reply == "Message sent."

    def test_caretaker_checkpoint_management_and_rollback(self):
        trace = TraceBuilder(7).with_reply("Original reply").build()
        originator = TraceOriginator(trace)
        caretaker = TraceCaretaker()

        caretaker.save_checkpoint("step_0", originator.create_memento("baseline"))

        originator.mutate_final_reply("First edit")
        caretaker.save_checkpoint("step_1", originator.create_memento("edit 1"))

        originator.mutate_final_reply("Second edit")
        caretaker.save_checkpoint("step_2", originator.create_memento("edit 2"))

        assert set(caretaker.list_checkpoints()) == {"step_0", "step_1", "step_2"}

        # Rollback to step 0
        originator.restore(caretaker.get_checkpoint("step_0"))
        assert originator.get_trace().reply == "Original reply"

        # Undo to step 2
        popped = caretaker.pop_last_checkpoint()
        assert popped.description == "edit 2"

    def test_counterfactual_confirmation_mutation_clears_violation(self):
        # Initial Trace 5 with unconfirmed send
        trace_5 = (
            TraceBuilder(5)
            .with_available_tools(["slack_send", "slack_ask_user_confirmation"])
            .with_tool_call("slack_send", request={"channel": "#engineering"}, result={"ok": True})
            .with_reply("Broadcasted to team.")
            .build()
        )

        pipeline = EvaluationPipeline()
        eval_before = pipeline.evaluate_trace(trace_5)
        assert eval_before.result == EvalVerdict.FAIL
        assert eval_before.is_release_blocker is True

        # Use Memento & Originator to construct counterfactual where confirmation occurred
        originator = TraceOriginator(trace_5)
        memento_original = originator.create_memento("failed_state")

        originator.add_confirmation_tool_call()
        counterfactual_trace = originator.get_trace()

        eval_after = pipeline.evaluate_trace(counterfactual_trace)
        assert eval_after.result == EvalVerdict.PASS
        assert eval_after.is_release_blocker is False

        # Verify rollback restores the original failing state cleanly
        originator.restore(memento_original)
        eval_restored = pipeline.evaluate_trace(originator.get_trace())
        assert eval_restored.result == EvalVerdict.FAIL
        assert eval_restored.is_release_blocker is True

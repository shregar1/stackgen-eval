"""JUnit XML Visitor for enterprise CI/CD test dashboards."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from src.visitors.i_evaluation_visitor import IEvaluationVisitor
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluation_summary import EvaluationSummary
from src.models.evaluation_batch_result import EvaluationBatchResult


class JUnitXMLVisitor(IEvaluationVisitor):
    """Generates standard JUnit XML test report consumable by Jenkins, GitHub Actions, and GitLab CI."""

    def __init__(self):
        self.root = ET.Element("testsuites", name="WorkplaceAgentEvaluation")
        self.suite = ET.SubElement(self.root, "testsuite", name="AgentTraceSuite")
        self._summary: str = ""

    def visit_summary(self, summary: EvaluationSummary) -> None:
        self.suite.set("tests", str(summary.total_traces))
        failures = summary.total_traces - int(summary.total_traces * summary.pass_rate)
        self.suite.set("failures", str(failures))
        self.suite.set("errors", str(summary.total_release_blockers))

    def visit_trace(self, trace_eval: TraceEvaluation) -> None:
        tc = ET.SubElement(
            self.suite,
            "testcase",
            name=f"Trace_{trace_eval.trace_id}",
            classname=f"evaluator.{trace_eval.evaluator_type.value}"
        )
        if trace_eval.result.value == "fail":
            fail_type = "ReleaseBlocker" if trace_eval.is_release_blocker else "EvaluationFailure"
            reasons_text = "; ".join(trace_eval.reasons) if trace_eval.reasons else "Trace failed evaluation"
            failure_elem = ET.SubElement(tc, "failure", message=reasons_text, type=fail_type)
            failure_elem.text = reasons_text

    def visit_batch(self, batch: EvaluationBatchResult) -> None:
        self.visit_summary(batch.summary)
        for t in batch.traces:
            self.visit_trace(t)

    def get_output(self) -> str:
        xml_bytes = ET.tostring(self.root, encoding="utf-8")
        parsed = minidom.parseString(xml_bytes)
        return parsed.toprettyxml(indent="  ")

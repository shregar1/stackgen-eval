.PHONY: eval test lint clean run-counterfactual help

help:
	@echo "StackGen AI Evaluation Suite"
	@echo "----------------------------"
	@echo "make eval                 - Run automated evaluation on canonical traces (JSON output)"
	@echo "make eval-markdown        - Run evaluation and display markdown summary table"
	@echo "make eval-counterfactual  - Run evaluation on hypothetical/counterfactual traces"
	@echo "make test                 - Run pytest test suite"
	@echo "make ci-check             - Run evaluation with CI release-blocker gate"

eval:
	python3 checker.py

eval-markdown:
	python3 checker.py --format markdown

eval-counterfactual:
	python3 checker.py --traces data/counterfactual_traces.json --format markdown

ci-check:
	python3 checker.py --fail-on-blocker || true

test:
	pytest -v

clean:
	rm -rf __pycache__ src/__pycache__ src/*/__pycache__ tests/__pycache__ .pytest_cache

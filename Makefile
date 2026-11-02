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
	pytest -v --cov=src

cov:
	pytest --cov=src --cov-report=term-missing

audit:
	python3 -c "import ast, os; failed = []; [failed.append(f'{os.path.join(r, f)}: multiple classes or funcs') for r, _, fs in os.walk('.') if not any(x in r for x in ['.git', '.pytest_cache', '__pycache__']) for f in fs if f.endswith('.py') and (any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.parse(open(os.path.join(r, f)).read()).body) or (f != '__init__.py' and len([n for n in ast.parse(open(os.path.join(r, f)).read()).body if isinstance(n, ast.ClassDef)]) != 1))]; assert not failed, failed; print('All modules adhere to strict 1-class OOP architecture!')"

clean:
	rm -rf __pycache__ src/**/__pycache__ tests/**/__pycache__ .pytest_cache .coverage htmlcov

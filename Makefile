.PHONY: help setup lint test run run-full clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "%-12s %s\n", $$1, $$2}'

setup:  ## Create a venv and install dev dependencies
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt

lint:  ## Run ruff on the Python tools
	ruff check bin tests

test:  ## Run the pytest suite
	pytest

run:  ## Run the pipeline on the bundled test data
	nextflow run . -profile docker,test --outdir results

run-full:  ## Run the on-demand real-data (E. coli) pipeline
	nextflow run . -profile docker,test_full --outdir results_full

clean:  ## Remove pipeline outputs and caches
	rm -rf results results_full run1 run2 work .nextflow* .nf-test .pytest_cache \
		bin/__pycache__ tests/__pycache__

.PHONY: setup lint graph test

setup:
	python3 -m pip install --upgrade pre-commit graphifyy detect-secrets -r requirements.txt
	pre-commit install --install-hooks
	graphify hook install
	graphify claude install

lint:
	pre-commit run --all-files

graph:
	graphify update .

test:
	python3 -m pytest -q

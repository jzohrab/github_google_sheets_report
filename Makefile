.PHONY: venv init test clean run

# Sample calls:
#   make PYTHON=/usr/local/bin/python3 venv
#   make PYTHON=`which python3` venv
# Create virtual env with specific python
# "--always-copy" added to work around Vagrant error for Windows,
# "OSError: [Errno 71] Protocol error:" (ref
# https://github.com/gratipay/gratipay.com/issues/2327)
venv:
	rm -rf venv
	virtualenv -p $(PYTHON) --always-copy venv

init:
	pip install -r requirements.txt

run:
	gunicorn myproject:app

test:
	python -m unittest tests/*.py

# Only useful during dev while things are thrashing!
# This should be removed.
create_test_expectations:
	python -m unittest tests/test_github_report.py > tests/data/expected_results/test_github_report.json

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm

.PHONY: venv init test clean

# Sample call: make PYTHON=/usr/local/bin/python3 venv
venv:
	rm -rf venv
	# Create virtual env with specific python
	virtualenv -p $(PYTHON) venv

init:
	pip install -r requirements.txt

test:
	nosetests tests

clean:
	rm -rf venv

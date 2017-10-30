.PHONY: venv init test clean

# Sample call: make PYTHON=/usr/local/bin/python3 venv
# Create virtual env with specific python
# "--always-copy" added to work around Vagrant error for Windows,
# "OSError: [Errno 71] Protocol error:" (ref
# https://github.com/gratipay/gratipay.com/issues/2327)
venv:
	rm -rf venv
	virtualenv -p $(PYTHON) --always-copy venv

init:
	pip install -r requirements.txt

test:
	nosetests tests

clean:
	rm -rf venv

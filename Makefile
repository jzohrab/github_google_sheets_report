.PHONY: venv init test clean

# Create virtual env with specific python
# (assuming that the machine/vm already has python3).
# "--always-copy" added to work around Vagrant error for Windows,
# "OSError: [Errno 71] Protocol error:" (ref
# https://github.com/gratipay/gratipay.com/issues/2327)
venv:
	virtualenv -p `which python3` --always-copy venv
	@echo '**********************'
	@echo Now please run the following:
	@echo   source venv/bin/activate
	@echo   make init
	@echo '**********************'

init:
	pip install -r requirements.txt

test:
	python -m unittest tests/*.py

clean:
	find . -name '*.pyc' -print0 | xargs -0 rm

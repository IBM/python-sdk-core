# This makefile is used to make it easier to get the project set up
# to be ready for development work in the local sandbox.
# example: "make setup"

PYTHON=python3
LINT_DIRS=ibm_cloud_sdk_core test test_integration

setup: deps dev_deps install_project

all: upgrade_pip setup test-unit lint

ci: setup test-unit lint

upgrade_pip:
	${PYTHON} -m pip install --upgrade pip

deps:
	${PYTHON} -m pip install -r requirements.txt

dev_deps:
	${PYTHON} -m pip install -r requirements-dev.txt

install_project:
	${PYTHON} -m pip install -e .

test-unit:
	${PYTHON} -m pytest --cov=ibm_cloud_sdk_core test

lint:
	${PYTHON} -m pylint ${LINT_DIRS}
	black --check ${LINT_DIRS}

lint-fix:
	black ${LINT_DIRS}

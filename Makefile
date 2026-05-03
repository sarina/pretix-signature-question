.PHONY: help localecompile localegen requirements lint test fix

# Put it first so that "make" without argument is like "make help".
PYTHON_VERSION := $(shell python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["requires-python"])')
help:
	@echo ""
	@echo "Required Python version: $(PYTHON_VERSION)"
	@echo ""
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

# --- Development environment ------------------------------------------------

# Tool lists, kept here so they live in one place and don't drift.
LINT_TOOLS  := isort flake8 black docformatter
TEST_TOOLS  := pytest pytest-django pytest-cov
BUILD_TOOLS := build twine check-manifest


# Installs pretix itself, the plugin in editable mode, plus all lint/test/build tooling.
requirements:  ## Bootstrap a development environment.  Run inside an activated virtualenv.
	pip install -U pip wheel setuptools
	pip install pretix
	pip install $(LINT_TOOLS) $(TEST_TOOLS) $(BUILD_TOOLS)
	pip install -Ue .

lint:  ## Run all linters in check mode (no auto-fix). Mirrors what CI runs.
	isort -c .
	flake8 .
	black --check .
	docformatter --check -r .

test:  ## Run pytest with coverage. Mirrors what CI runs.
	pytest --cov=pretix_signature_capture tests

fix:  ## Runs isort, black, and docformatter to autofix linting issues
	isort . && black . && docformatter -r .

# --- Translation targets ----------------------------------------------------
# NOTE: translation support is currently disabled for the 2.0 release; running
# these requires a working `compilemessages` invocation, which is broken under
# modern PEP 517 builds. See:
#   https://github.com/sarina/pretix-signature-question/issues/18

LNGS:=`find pretix_signature_capture/locale/ -mindepth 1 -maxdepth 1 -type d -printf "-l %f "`

localecompile:  ## BROKEN (issue #18): Compile messages for i18n
	django-admin compilemessages

localegen:  ## BROKEN (issue #18): Make messages for l10n
	django-admin makemessages --keep-pot -i build -i dist -i "*egg*" $(LNGS)



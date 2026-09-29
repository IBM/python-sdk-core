# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Commands
```bash
# Setup & install in editable mode with dev dependencies
make setup                     # or: pip install -e .[dev]

# Run all unit tests with coverage
make test-unit                 # python3 -m pytest --cov=ibm_cloud_sdk_core test

# Run a single test file or specific test case
pytest test/test_base_service.py
pytest test/test_base_service.py::test_custom_headers

# Run integration tests (requires live IBM Cloud credentials)
pytest test_integration/

# Linting & formatting
make lint                      # pylint ibm_cloud_sdk_core test test_integration && black --check ...
make lint-fix                  # black ibm_cloud_sdk_core test test_integration

# Secrets scanning (enforced in CI)
detect-secrets scan --update .secrets.baseline
```

## Non-Obvious Architecture & Conventions
- **Black formatting**: `line-length = 120`, `skip-string-normalization = true` (preserves single quotes `'`).
- **File header**: Every Python file requires `# coding: utf-8` on line 1 followed by IBM copyright notice.
- **External config priority**: `read_external_sources(service_name)` resolves configuration in order: (1) `IBM_CREDENTIALS_FILE` / `./ibm-credentials.env` / `~/.ibm-credentials.env`, (2) Environment variables (`<SERVICE_NAME>_<PROP>`), (3) VCAP Services.
- **Auto-auth fallback**: If `AUTH_TYPE` is omitted, defaults to `IAM` if `APIKEY` is present, otherwise defaults to `CONTAINER`.
- **ApiException status**: Use `status_code` attribute on `ApiException`; accessing `.code` raises `DeprecationWarning`.
- **Logging & Redaction**: Use `get_logger()` from `ibm_cloud_sdk_core.logger`. `LoggingFilter` automatically redacts sensitive keywords matching `REDACTED_KEYWORDS` (e.g. apikey, token, secret, password).
- **Test server fixture**: Use `@local_server(port=..., tls_version=...)` from `test.utils.http_utils` to spin up a mock HTTP/HTTPS background thread in unit tests.

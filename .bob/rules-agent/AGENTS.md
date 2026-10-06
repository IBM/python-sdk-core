# Project Coding Rules (Non-Obvious Only)

- **Quotes & Black**: Always run `black` with `--line-length 120 --skip-string-normalization` (or `make lint-fix`). Do not convert single quotes `'` to double quotes `"` unnecessarily.
- **File headers**: New Python files must start with `# coding: utf-8` on line 1 followed by the IBM Apache 2.0 license comment block.
- **Exception attributes**: When checking or raising `ApiException`, always use `.status_code`. Avoid `.code` as it triggers a deprecation warning.
- **Config resolution**: Always use `read_external_sources(service_name)` or `get_authenticator_from_environment(service_name)` for external credentials rather than directly reading environment variables.
- **Logging secrets**: Never bypass `ibm_cloud_sdk_core.logger.get_logger()` with raw `print` statements in core code; debug HTTP traffic is automatically redacted via `LoggingFilter.filter_message()`.
- **Test helpers**: For socket / TLS tests, wrap test methods with `@local_server` from `test.utils.http_utils` instead of creating ad-hoc socket listeners.

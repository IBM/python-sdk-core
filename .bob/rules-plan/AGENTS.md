# Project Architecture Rules (Non-Obvious Only)

- **Authentication architecture**: Authenticators in `ibm_cloud_sdk_core/authenticators/` wrap corresponding TokenManagers in `ibm_cloud_sdk_core/token_managers/` which handle JWT validation, token caching, and automated refresh lifecycles.
- **Auto auth detection**: Omitting `AUTH_TYPE` in configuration defaults to `IAM` if `APIKEY` is present, or `CONTAINER` otherwise.
- **SSL adapter layering**: `BaseService` mounts custom `SSLHTTPAdapter` onto `requests.Session` for both `http://` and `https://` to handle SSL verification disabling across custom pools.
- **Payload compression**: `GzipStream` (`ibm_cloud_sdk_core/utils.py`) streams and compresses file-like objects on the fly without reading the entire payload into memory.
- **Versioning & Releases**: Uses `semantic-release` via `package.json` in GitHub Actions; commit messages must follow conventional commits for automated version bumping.

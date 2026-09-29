# Project Documentation Context (Non-Obvious Only)

- **Library purpose**: `ibm_cloud_sdk_core` is the shared base runtime for all IBM Cloud generated Python SDKs (e.g., Watson, VPC, Platform services). It is not an end-user service SDK by itself.
- **`Authentication.md` vs `README.md`**: `Authentication.md` contains detailed reference documentation and env var configurations for all supported authenticators (IAM, CP4D, Container/IKS, VPC, MCSP/MCSPv2).
- **External config lookup precedence**: `ibm-credentials.env` in current directory takes precedence over environment variables, which take precedence over VCAP Services (Cloud Foundry legacy).
- **Generated code integration**: `BaseService` is the parent class for SDK generated services; parameters and response parsing in `BaseService` dictate generated SDK client behavior across the ecosystem.

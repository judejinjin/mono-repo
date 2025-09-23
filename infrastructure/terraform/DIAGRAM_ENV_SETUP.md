# Environment Setup for Terraform Diagram Generation

This project supports fast, local diagram generation for Terraform infrastructure without hardcoding sensitive values or AMI IDs. All credentials and AMI IDs are loaded from environment variables, making it easy to switch between real deployments and static/demo diagrams.

## How It Works
- **AMI ID Selection:**
  - If `TF_DIAGRAM_MODE=1` is set, Terraform uses the static AMI ID from `STATIC_AMI_ID` (default: `ami-12345678`).
  - For real deployments, set `DEV_SERVER_AMI_ID` to your desired AMI ID, or let Terraform use the latest Ubuntu AMI via the data source.
- **AWS Credentials:**
  - All AWS credentials should be set in your environment or `.env` file (e.g., `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`).

## Example `.env` for Diagram Generation (using TF_VAR_ pattern)
```
TF_VAR_diagram_mode=1
TF_VAR_static_ami_id=ami-12345678
AWS_ACCESS_KEY_ID=dummy
AWS_SECRET_ACCESS_KEY=dummy
AWS_DEFAULT_REGION=us-east-1
```

## Example `.env` for Real Deployment
```
TF_VAR_diagram_mode=0
TF_VAR_dev_server_ami_id=ami-xxxxxxxx
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## Usage
1. Create your `.env` file in the Terraform directory.
2. Source the environment before running diagram scripts:
  ```bash
  set -a
  source .env
  set +a
  ./generate-diagrams.sh
  ```
3. For real deployments, set `TF_DIAGRAM_MODE=0` and provide real credentials and AMI IDs.

## Notes
- No AMI IDs or credentials are hardcoded in Terraform files.
- The same pattern can be extended to other resources and environments. Just add a variable in Terraform and set it via `TF_VAR_` in your `.env`.
- For CI/CD, set environment variables in your pipeline config.

---
For questions, see this file or contact the repo maintainer.

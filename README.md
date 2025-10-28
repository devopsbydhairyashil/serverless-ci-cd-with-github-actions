# serverless-ci-cd-with-github-actions

Automated CI/CD pipeline for a small serverless application (AWS Lambda + API Gateway) using GitHub Actions and AWS SAM.
This expanded guide provides step-by-step deployment instructions, a Terraform snippet for infrastructure (optional),
and example CloudFormation/SAM parameters used by the workflow.

---

## Prerequisites (local)
- AWS CLI configured with credentials that can create Lambda, IAM roles, CloudFormation stacks.
- AWS SAM CLI installed (`sam`).
- Python 3.9+ and pip.
- (Optional) Terraform v1.3+ if using the provided Terraform snippet.
- GitHub repository with Actions enabled and secrets configured:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION` (e.g., us-east-1)

---

## Directory layout (key files)
```
src/
  handler.py
  requirements.txt
template.yaml               # SAM template
.github/workflows/deploy.yml
scripts/bootstrap.sh
docs/architecture.md
events/event.json           # example event for local invoke (create if not present)
```

---

## Quick local test (developer)
1. Create a Python virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
```
2. Build and invoke locally:
```bash
sam build
sam local invoke HelloFunction --event events/event.json
```
3. Run the function locally via API Gateway emulation:
```bash
sam local start-api
# then visit http://127.0.0.1:3000/hello
```

---

## Deploy with SAM (manual)
1. Package the application (uploads artifacts to S3):
```bash
aws s3 mb s3://my-sam-artifacts-bucket --region us-east-1 || true
sam package --output-template-file packaged.yaml --s3-bucket my-sam-artifacts-bucket
```
2. Deploy the stack (create or update CloudFormation stack):
```bash
sam deploy --template-file packaged.yaml --stack-name myservice-staging --capabilities CAPABILITY_NAMED_IAM --region us-east-1 --parameter-overrides Environment=staging
```
3. To view logs:
```bash
aws logs tail /aws/lambda/<stack-name>-HelloFunction --follow
```

---

## GitHub Actions workflow (notes)
The included workflow at `.github/workflows/deploy.yml` follows this flow:
- checkout code
- set up Python and SAM
- run unit tests (if any)
- build and run `sam deploy` using the branch name as stack suffix
The workflow expects the repository secrets `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and optionally `AWS_REGION`.

---

## Terraform snippet (optional) — create S3 bucket and DynamoDB lock for remote state
Below is a minimal Terraform configuration to create an S3 bucket and DynamoDB table for locking state.
Use this if you want to store Terraform remote state for other infra pieces in the repo.
```hcl
terraform {
  required_version = ">= 1.0"
  backend "s3" {
    bucket = "tf-state-demo-bucket-12345"
    key    = "serverless-ci-cd/state.tfstate"
    region = "us-east-1"
    dynamodb_table = "tf-state-lock"
    encrypt = true
  }
}

resource "aws_s3_bucket" "tfstate" {
  bucket = "tf-state-demo-bucket-12345"
  acl    = "private"
  versioning { enabled = true }
}

resource "aws_dynamodb_table" "lock" {
  name           = "tf-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}
```

---

## Example minimal SAM parameters (CloudFormation parameters)
When deploying through CI, the following parameter set is recommended for environment separation:
- `Environment`: `staging` or `production`
- `LogRetentionInDays`: `30`
- `XRayTracingEnabled`: `true`

The Actions workflow uses `sam deploy --no-confirm-changeset --stack-name demo-${{ github.ref_name }} --capabilities CAPABILITY_NAMED_IAM`.
Adjust the stack name and parameter overrides as needed for your account.

---

## Post-deploy verification
1. Get stack outputs:
```bash
aws cloudformation describe-stacks --stack-name myservice-staging --query "Stacks[0].Outputs" --output table
```
2. Exercise API endpoint returned in outputs (curl or browser).
3. Check CloudWatch Logs and X-Ray traces for the new invocation.
4. Confirm IAM roles created have only the permissions required for the function runtime.

---

## Rollback and safe practices
- Use versioned S3 artifact buckets to avoid accidental overwrites.
- Test deployments first to a `staging` branch that maps to `staging` stack.
- Use CloudFormation stack policies when modifying critical resources.

---

Connect with me on LinkedIn: https://www.linkedin.com/in/dhairyashil-bhosale


---

License: MIT. See LICENSE file.

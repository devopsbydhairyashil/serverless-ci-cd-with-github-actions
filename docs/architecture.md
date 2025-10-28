# Architecture

A small API fronted by API Gateway that invokes a Lambda function. Deployment is automated with GitHub Actions using AWS SAM.
Logs flow to CloudWatch and X-Ray is enabled for distributed tracing.

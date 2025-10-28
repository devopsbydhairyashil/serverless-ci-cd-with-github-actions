import json
def lambda_handler(event, context):
    # simple handler used for CI/CD demo
    body = {"message": "Hello from serverless-ci-cd-with-github-actions"}
    return {"statusCode": 200, "body": json.dumps(body)}

import boto3
import json
import time

CF = boto3.client("cloudformation")

def deploy_stack(stack_name, template_s3, parameters, capabilities):
    """Create or update a stack from S3 template"""
    template_url = template_s3.replace("s3://", "https://s3.amazonaws.com/")
    cfn_params = [{"ParameterKey": k, "ParameterValue": str(v)} for k, v in parameters.items()]

    try:
        CF.describe_stacks(StackName=stack_name)
        print(f"Updating stack {stack_name} ...")
        resp = CF.update_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Parameters=cfn_params,
            Capabilities=capabilities,
        )
        status = "update_started"
    except CF.exceptions.ClientError as e:
        if "does not exist" in str(e):
            print(f"Creating stack {stack_name} ...")
            resp = CF.create_stack(
                StackName=stack_name,
                TemplateURL=template_url,
                Parameters=cfn_params,
                Capabilities=capabilities,
            )
            status = "create_started"
        elif "No updates are to be performed" in str(e):
            print(f"No updates required for {stack_name}.")
            return {"status": "no_change", "StackName": stack_name}
        else:
            raise

    stack_id = resp["StackId"]
    print(f"{status}: {stack_id}")
    return {"status": status, "StackId": stack_id}


def lambda_handler(event, _context):
    """Main Lambda entry"""
    results = []
    try:
        # Deploy Infra stack first
        infra_template = event["InfraTemplateS3"]
        infra_params = event["InfraParameters"]
        infra_stack = event.get("InfraStackName", "iris-mlops-infra")
        results.append(deploy_stack(infra_stack, infra_template, infra_params, event["Capabilities"]))

        # Wait a bit (optional: poll status)
        time.sleep(20)

        # Get outputs from infra stack (LogGroupArn, RoleStepFunctionsArn)
        desc = CF.describe_stacks(StackName=infra_stack)["Stacks"][0]
        outputs = {o["OutputKey"]: o["OutputValue"] for o in desc.get("Outputs", [])}
        print("Infra outputs:", outputs)

        # Deploy Pipeline stack using outputs
        pipeline_params = event["PipelineParameters"]
        pipeline_params["StepFnLogGroupArn"] = outputs["StepFnLogGroupArn"]
        pipeline_params["RoleStepFunctionsArn"] = outputs["RoleStepFunctionsArn"]

        results.append(
            deploy_stack(
                event["PipelineStackName"],
                event["PipelineTemplateS3"],
                pipeline_params,
                event["Capabilities"],
            )
        )
        return {"status": "ok", "stacks": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# For local CLI testing
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--infra-template", required=True)
    parser.add_argument("--pipeline-template", required=True)
    parser.add_argument("--bucket", required=True)
    args = parser.parse_args()

    event = {
        "InfraStackName": "iris-mlops-infra",
        "PipelineStackName": "iris-mlops-pipeline",
        "InfraTemplateS3": args.infra_template,
        "PipelineTemplateS3": args.pipeline_template,
        "InfraParameters": {
            "ProjectName": "iris-mlops",
            "SageMakerRoleArn": "arn:aws:iam::182406535835:role/service-role/AmazonSageMaker-ExecutionRole-20251013T175169",
        },
        "PipelineParameters": {
            "ProjectName": "iris-mlops",
            "ECRImageURI": "182406535835.dkr.ecr.eu-north-1.amazonaws.com/sagemaker-studio-d-x5rfkjrvcd2t:default-20251013T175168",
            "S3BucketName": "iris-mlops-bucket-182406535835",
            "SageMakerRoleArn": "arn:aws:iam::182406535835:role/service-role/AmazonSageMaker-ExecutionRole-20251013T175169",
        },
        "Capabilities": ["CAPABILITY_NAMED_IAM"],
    }

    print(json.dumps(lambda_handler(event, None), indent=2))

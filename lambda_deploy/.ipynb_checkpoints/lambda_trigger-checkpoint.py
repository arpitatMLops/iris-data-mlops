import boto3

CF = boto3.client("cloudformation")

def lambda_handler(event, _context):
    
    stack = event["StackName"]
    tpl = event["TemplateS3"]
    params = event.get("Parameters", {})
    caps = event.get("Capabilities", [])

    template_url = tpl.replace("s3://", "https://s3.amazonaws.com/")

    cfn_params = [{"ParameterKey": k, "ParameterValue": str(v)} for k, v in params.items()]

    try:
        # If stack exists → update, else create
        try:
            CF.describe_stacks(StackName=stack)
            resp = CF.update_stack(StackName=stack,
                                   TemplateURL=template_url,
                                   Parameters=cfn_params,
                                   Capabilities=caps)
            return {"status": "update_started", "StackId": resp.get("StackId")}
        except CF.exceptions.ClientError as e:
            msg = str(e)
            if "does not exist" in msg:
                resp = CF.create_stack(StackName=stack,
                                       TemplateURL=template_url,
                                       Parameters=cfn_params,
                                       Capabilities=caps)
                return {"status": "create_started", "StackId": resp.get("StackId")}
            else:
                raise
    except Exception as err:
        return {"status": "error", "message": str(err)}

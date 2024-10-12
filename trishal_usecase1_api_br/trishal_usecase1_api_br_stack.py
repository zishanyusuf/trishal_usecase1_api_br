from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    RemovalPolicy
    # aws_sqs as sqs,
)
import json
from constructs import Construct

class TrishalUsecase1ApiBrStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create the S3 bucket to store images. The name of the S3 bucket is "ImageBucket"
        my_bucket = s3.Bucket(
            self, 
            "movie-posterdesign01",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
             auto_delete_objects=True # This will delete the bucket on stack deletion
            )
        
        # 2. Create the Lambda function
        lambda_function = _lambda.Function(self, "moviePosterDesignFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            code=_lambda.Code.from_asset("./function_code"),
            # layers=[layer],
            timeout=Duration.seconds(63),
            environment={
                "BUCKET_NAME": my_bucket.bucket_name
            }
            )
        
        
        
        #3. Define permissions 3.1. Define a policy to access the specific LLM model 3.2. Attach this policy to Lambda to be able to invoke the LLM model
        # 3.3.  Grant permissions to the Lambda to upload an image in the S3 Bucket 
        # invoke_model_policy = iam.Policy(self, "InvokeModelPolicy",
        #     statements=[
        #         iam.PolicyStatement(
        #             actions=["bedrock:InvokeModel"],
        #             resources=[f"arn:aws:bedrock:{self.region}::foundation-model/stability.stable-diffusion-xl-v1"]
        #         )
        #     ]
        # )
        # invoke_model_policy.attach_to_role(lambda_function.role)

        # Create an IAM policy for Bedrock access
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'bedrock:InvokeModel',
                'bedrock:ListFoundationModels',
                # Add other Bedrock actions as needed
            ],
            resources=['*']  # You might want to restrict this to specific Bedrock resources
        )

        # Add the Bedrock policy to the Lambda function's role
        lambda_function.add_to_role_policy(bedrock_policy)

        # my_bucket.grant_put(lambda_function)
        # my_bucket.grant_read_write(lambda_function)

        # Alternatively, if you need full access to all S3 actions, use this:
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:*"],
            resources=["*"]
        ))
        
        #4. Define the API Gateway
        #create api gateway with "regional" Endpoint type. Default is "EDGE"
        api = apigw.RestApi(self, "CDKmoviePosterAPI", 
                            endpoint_configuration=apigw.EndpointConfiguration(
                                types=[apigw.EndpointType.REGIONAL]
                                )
                            )
        
     
        #create a new resource
        text_gen_resource = api.root.add_resource("moviePosterAPIDesign")
        text_gen_resource.add_method("GET", 
                                     apigw.LambdaIntegration(
                                          lambda_function,
                                          proxy=False,
                                          integration_responses=[
                                             apigw.IntegrationResponse(
                                                 status_code="200",
                                                 response_templates={"application/json": ''}
                                            )
                                          ],
                                          request_templates={
                                            "application/json": json.dumps(
                                            {
                                            "prompt": "$input.params('prompt')"
                                            })
                                           }
                                          ),
                                               
                                    request_validator_options=apigw.RequestValidatorOptions(
                                        request_validator_name="Validate query string parameters and headers",
                                        validate_request_body=True,
                                        validate_request_parameters=True
                                        ),
                                    method_responses=[apigw.MethodResponse(status_code="200")],
                                    request_parameters={
                                        "method.request.querystring.prompt": True  # Required parameter
                                    }
                                )

        # 5. Output the API URL
        self.api_url = api.url
                                    
        
import aws_cdk as core
import aws_cdk.assertions as assertions

from trishal_usecase1_api_br.trishal_usecase1_api_br_stack import TrishalUsecase1ApiBrStack

# example tests. To run these tests, uncomment this file along with the example
# resource in trishal_usecase1_api_br/trishal_usecase1_api_br_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TrishalUsecase1ApiBrStack(app, "trishal-usecase1-api-br")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

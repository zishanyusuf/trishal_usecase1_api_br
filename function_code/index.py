#1. Import all libraries
import json
import boto3
import base64
import datetime
import os
#2. Test if boto3 version is later than 1.28.63. The later version ensures access of the LLM models, else we would need to add a layer.
print("The boto3 version is: " + boto3.__version__ + " and it should be later than 1.28.63")

#3. Create client connection for Lambda to Bedrock and S3. This will help lambda to make a call to Bedrock and S3 for all purposes
client_bedrock = boto3.client('bedrock-runtime')
client_s3 = boto3.client('s3')

#4. Define the lambda handler function 4.1. Store the input data (prompt) in a variable
def lambda_handler(event, context):
    s3bucket_name = os.environ['BUCKET_NAME']
    input_prompt=event['prompt']
    print(input_prompt)

#4. Create a request syntax to access the Bedrock LLM Model. Pass the prompt variable and get the response
    response_bedrock = client_bedrock.invoke_model(contentType='application/json', accept='application/json', 
    modelId='stability.stable-diffusion-xl-v1',
    # trace='ENABLED',
    # guardrailIdentifier='string',
    # guardrailVersion='string',
    body=json.dumps({
        "text_prompts": [
            {"text": input_prompt}],
            "cfg_scale": 10,
            "steps": 30,
            "seed": 0
            })
    )

#5. 5a. Retreive from Dictionary, 5b. Convert Streaming Body to Byte using json load 5c. Print
    response_bedrock_byte=json.loads(response_bedrock.get("body").read())
    # print(response_bedrock_byte['result'])

#6. 6a. Retreive data with artifact key, 6b. Import Base 64, 6c. Decode from Base64
    response_bedrock_base64 = response_bedrock_byte.get("artifacts")[0].get("base64")
    # base64_image = response_body.get("artifacts")[0].get("base64")
    # print(response_bedrock_base64)
    response_bedrock_finalimage = base64.b64decode(response_bedrock_base64)
    print(response_bedrock_finalimage)
    
#7. 7a. Upload the File to S3 using Put Object Method - Link 7b. Import datetime 7c. Generate the image name to be stored in S3 - Link
    poster_name = 'posterName' + datetime.datetime.today().strftime('%Y-%M-%D-%M-%S')
    response_s3 = client_s3.put_object(
        # Bucket = "movie-posterdesign01",
        Bucket = s3bucket_name,
        Body=response_bedrock_finalimage,
        Key=poster_name
        )

#8. Generate a presigned URL of the generated image
    generate_presigned_url = client_s3.generate_presigned_url(
        'get_object', 
        Params={
            # "Bucket": 'movie-posterdesign01',
            "Bucket": s3bucket_name, 
            "Key": poster_name
        }, 
        ExpiresIn=3600
    )
    print(generate_presigned_url)
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': generate_presigned_url
    }
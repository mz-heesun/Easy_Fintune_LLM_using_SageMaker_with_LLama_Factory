import time

import boto3
import sagemaker
from sagemaker import image_uris
from sagemaker.utils import name_from_base

iam_client = boto3.client('iam')

# Get the role ARN by its name
role_name = "SageMakerExecutionRole"
role = iam_client.get_role(RoleName=role_name)['Role']['Arn']
sess = sagemaker.session.Session()  # sagemaker session for interacting with different AWS APIs
default_bucket = sess.default_bucket()  # bucket to house artifacts

region = sess._region_name
account_id = sess.account_id()

s3_client = boto3.client("s3")
sm_client = boto3.client("sagemaker")
smr_client = boto3.client("sagemaker-runtime")

inference_image_uri = image_uris.retrieve(
    framework="djl-lmi",
    region=sess.boto_session.region_name,
    version="0.29.0"
)

print(f"Image going to be used is ---- > {inference_image_uri}")


s3_code_prefix = "llm_finetune/llama-3-8b-qlora"
print(f"s3_code_prefix: {s3_code_prefix}")

s3_code_artifact = sess.upload_data("model.tar.gz", default_bucket, s3_code_prefix)
print(f"S3 Code or Model tar ball uploaded to --- > {s3_code_artifact}")

model_name = name_from_base(f"llama3-8b-qlora").replace('.', '-').replace('_', '-')
print(model_name)
print(f"Image going to be used is ---- > {inference_image_uri}")

create_model_response = sm_client.create_model(
    ModelName=model_name,
    ExecutionRoleArn=role,
    PrimaryContainer={
        "Image": inference_image_uri,
        "ModelDataUrl": s3_code_artifact
    },

)
model_arn = create_model_response["ModelArn"]

print(f"Created Model: {model_arn}")

endpoint_config_name = f"{model_name}-config"
endpoint_name = f"{model_name}-endpoint"

#Note: ml.g4dn.2xlarge 也可以选择
endpoint_config_response = sm_client.create_endpoint_config(
    EndpointConfigName=endpoint_config_name,
    ProductionVariants=[
        {
            "VariantName": "variant1",
            "ModelName": model_name,
            "InstanceType": "ml.g5.2xlarge",
            "InitialInstanceCount": 1,
            # "VolumeSizeInGB" : 400,
            # "ModelDataDownloadTimeoutInSeconds": 2400,
            "ContainerStartupHealthCheckTimeoutInSeconds": 10 * 60,
        },
    ],
)
print(f"Endpoint Config Response: {endpoint_config_response}")

create_endpoint_response = sm_client.create_endpoint(
    EndpointName=f"{endpoint_name}", EndpointConfigName=endpoint_config_name
)
print(f"Created Endpoint: {create_endpoint_response['EndpointArn']}")

resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
status = resp["EndpointStatus"]
print("Status: " + status)

while status == "Creating":
    time.sleep(60)
    resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
    status = resp["EndpointStatus"]
    print("Status: " + status)

print("Arn: " + resp["EndpointArn"])
print("Status: " + status)
print("EndpointName: " + endpoint_name)
print("EndpointConfigName: " + endpoint_config_name)
print("ModelName: " + model_name)
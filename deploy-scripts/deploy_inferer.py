import time

import boto3
import sagemaker
from sagemaker import image_uris
from sagemaker.utils import name_from_base


def create_endpoint_config(model_name, endpoint_config_name):
    # Note: ml.g4dn.2xlarge 也可以选择
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
    return endpoint_config_response


def create_endpoint(endpoint_name, endpoint_config_name):
    create_endpoint_response = sm_client.create_endpoint(
        EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name
    )
    print(f"Created Endpoint: {create_endpoint_response['EndpointArn']}")
    return create_endpoint_response


def get_endpoint_status(endpoint_name):
    resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
    return resp["EndpointStatus"]


def get_inference_image_uri():
    return image_uris.retrieve(
        framework="djl-lmi",
        region=sess.boto_session.region_name,
        version="0.29.0"
    )


def get_role_arn(role_name: str):
    return iam_client.get_role(RoleName=role_name)['Role']['Arn']


def setup_model(s3_code_prefix: str, default_bucket):
    inference_image_uri = get_inference_image_uri()
    print(f"사용하게 될 inference IMAGE URI ---- > {inference_image_uri}")
    s3_code_artifact = sess.upload_data("model.tar.gz", default_bucket, s3_code_prefix)
    print(f"S3에 모델, tar파일이 업로드됨 --- > {s3_code_artifact}")
    model_name = name_from_base(f"llama3-8b-qlora").replace('.', '-').replace('_', '-')
    return (inference_image_uri, s3_code_artifact, model_name)


def create_model(inference_image_uri, s3_code_artifact):
    create_model_response = sm_client.create_model(
        ModelName=model_name,
        ExecutionRoleArn=role,
        PrimaryContainer={
            "Image": inference_image_uri,
            "ModelDataUrl": s3_code_artifact
        },

    )
    print(f"Model Response: {create_model_response}")
    return create_model_response


if __name__ == "__main__":
    # setup
    sess = sagemaker.session.Session()
    iam_client = boto3.client('iam')
    s3_client = boto3.client("s3")
    sm_client = boto3.client("sagemaker")
    smr_client = boto3.client("sagemaker-runtime")

    # 해당 부분이 오류가 발생한다면 README.md의 2번째 단락을 참고해주세요
    role = get_role_arn(role_name="SageMakerExecutionRole")

    # 필수정보 로드
    default_bucket = sess.default_bucket()
    region = sess._region_name
    account_id = sess.account_id()
    print(f"Default Bucket: {default_bucket}")
    print(f"Region: {region}")
    print(f"Account ID: {account_id}")

    # 모델을 생성하기 전에 훈련된 내용을 가지고 모델파일을 만들어줘야합니다.
    s3_code_prefix = "llm_finetune/llama-3-8b-qlora"
    (inference_image_uri, s3_code_artifact, model_name) = setup_model(s3_code_prefix, default_bucket)

    # 모델 생성
    train_model = create_model(inference_image_uri, s3_code_artifact)

    # 모델 필수정보 로드
    model_arn = train_model["ModelArn"]
    endpoint_config_name = f"{model_name}-config"
    endpoint_name = f"{model_name}-endpoint"

    # 엔드포인트 구성정보 생성
    create_endpoint_config(model_name, endpoint_config_name)

    # 엔드포인트 생성
    create_endpoint(endpoint_name, endpoint_config_name)

    # 엔드포인트 생성될 때 까지 기다림
    while (status := get_endpoint_status(endpoint_name)) == "Creating":
        time.sleep(60)
        print("Status: " + status)

    resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
    print("Arn: " + resp["EndpointArn"])
    print("Status: " + status)
    print("EndpointName: " + endpoint_name)
    print("EndpointConfigName: " + endpoint_config_name)
    print("ModelName: " + model_name)

    # call_endpoint.py 에서 ModelName을 가지고 테스트를 진행해봅니다.

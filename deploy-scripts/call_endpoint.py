import json
import boto3

smr_client = boto3.client("sagemaker-runtime")
parameters = {
    "max_new_tokens": 512,
    "temperature": 0.9,
    "top_p": 0.8
}

endpoint_name = "llama3-8b-qlora-2024-11-21-09-18-00-310-endpoint"

messages = [
    {"role": "system", "content": "항상 한국말로 대답해주세요"},
    {"role": "user", "content": "왜요?"},
]

invoke_response = smr_client.invoke_endpoint(
    EndpointName=endpoint_name,
    Body=json.dumps(
        {
            "messages": messages,
            "stream": False,
            **parameters,
        }
    ),
    ContentType="application/json",
    CustomAttributes='accept_eula=false'
)

print(json.loads(invoke_response["Body"].read().decode("utf-8"))['choices'][0]['message'])

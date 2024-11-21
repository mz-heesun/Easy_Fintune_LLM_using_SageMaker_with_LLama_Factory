# 배포하기 스크립트



### 커스텀 SageMakerRole 생성
```shell
aws iam create-role --role-name SageMakerExecutionRole --assume-role-policy-document file://./policy/sagemaker-endpoint-policy.json
aws iam attach-role-policy --role-name SageMakerExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
```

### 모델 만들기
결과를 로컬로 가져와 배포하기
```shell
aws s3 sync s3://sagemaker-us-east-2-529075693336-2/hyperpod/llama3-8b-qlora/finetuned_model/ ./vllm_inference/adapters/exp
rm -rf ./vllm_inference/adapters/exp/checkpoint*
rm -rf ./vllm_inference/adapters/exp/runs
```

압축해서 tar.gz 파일로 만들기 
```shell
tar czvf ./model.tar.gz ./vllm_inference
```

### 모델을 엔드포인트로 배포하기 
```shell
python deploy_inferer.py
## 마지막에 endpoint name값을 기억할 것
```

### 엔드포인트를 호출해보기
```shell
python call_endpoint.py
```




---

### 엔드포인트 정리하기
```shell
!aws sagemaker delete-endpoint --endpoint-name {endpoint_name}
!aws sagemaker delete-endpoint-config --endpoint-config-name {endpoint_config_name}
!aws sagemaker delete-model --model-name {model_name}
```
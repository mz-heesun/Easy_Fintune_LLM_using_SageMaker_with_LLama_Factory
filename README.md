### LLaMA Factory Project

참고자료 
1. [LLaMA Factory-HyperPod Document](https://aws.amazon.com/cn/blogs/china/easily-fine-tune-large-models-using-llama-factory-on-sagemaker-hyperpod/)
2. [LLaMA Factory-HyperPod Github](https://github.com/mz-heesun/Easy_Fintune_LLM_using_SageMaker_with_LLama_Factory)
3. [LLaMA Factory Github](https://github.com/hiyouga/LLaMA-Factory)
4. [HyperPod Instance type, pricing](https://aws.amazon.com/ko/sagemaker/pricing/)


목적 
- LLaMA Factory 프로젝트를 사용하여 HyperPod를 통한 모델 학습을 진행하는 프로젝트

주의사항
- M1 MacOS에서 실행한 내용입니다.
- 참고자료[2] 의 내용을 기준으로 새롭게 작성하였습니다.
- 우리 상황에 알맞게 코드를 수정하였습니다.
- Mulit GPU를 사용하려면 P5, P4, Trn1 타입 인스턴스를 사용해야합니다.
- Single GPU는 g5 계열을 사용합니다
- Intel Chipset은 t3, m5, c5 계열을 사용합니다.


## 선수작업
AWS Configure Setting
- 프로파일 생성
```shell
aws configure --profile 생성할_profile_name
```
- 프로파일 목록 확인
```shell
aws configure list-profiles
'''
default
atomy
shinhan-mycar
source-account
target-account
pentacle
'''
```
- 생성한 프로파일 선택
```shell
export AWS_PROFILE=생성한_profile_name
# export AWS_PROFILE=pentacle
```

---

### 기본 버킷 생성
```shell
export BUCKET=사용하고싶은_bucket_name
export REGION=사용하고싶은 region
# export BUCKET=sagemaker-us-east-2-529075693336-2
# export REGION=us-east-2
```
role 생성
```shell
aws iam create-role --role-name LLaMAFactoryS3Role --assume-role-policy-document file://$(pwd)/policies/trust_policy.json
aws iam put-role-policy --role-name LLaMAFactoryS3Role --policy-name S3PutObjectPolicy --policy-document file://$(pwd)/policies/bucket_policy.json
```

s3 생성
```shell

aws s3api create-bucket --bucket ${BUCKET} --region ${REGION} --create-bucket-configuration LocationConstraint=${REGION}
aws s3api put-bucket-policy --bucket ${BUCKET} --policy file://$(pwd)/policies/put_bucket_policy.json
#aws s3api put-bucket-policy --bucket ${BUCKET} --policy file://$(pwd)/bucket_policy.json
```

### lifecycle-scripts 업로드
```shell
aws s3 cp —recursive lifecycle-scripts/ s3://${BUCKET}/hyperpod/LifecycleScripts/
```

### HyperPod Cluster 생성
```shell
# Single GPU Version
# 해당 파일을 열어 cluster name을 가져올 것 
aws sagemaker create-cluster --cli-input-json file://$(pwd)/create_cluster_single_gpu.json
# 15분정도 생성시간이 소요됨.
# Multi GPU Version
# aws sagemaker create-cluster --cli-input-json ./create_cluster_multi_gpu.json
```

업로드 LLaMA Factory Source, Resources
```shell
# ./s5cmd sync ./LLaMA-Factory s3://${BUCKET}/hyperpod/
aws s3 cp --recursive hyperpod-scripts/ s3://${BUCKET}/hyperpod/LLaMA-Factory/
aws s3 cp --recursive LLaMA-Factory/data s3://${BUCKET}/dataset-for-training/train/
aws s3 cp --recursive training-data/ s3://${BUCKET}/dataset-for-training/train/
```

### HyperPod Cluster에 대한 원격 엑세스 설정
[SSM 설치](https://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/install-plugin-macos-overview.html)
```shell
#m1 apple
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac_arm64/sessionmanager-bundle.zip" -o "sessionmanager-bundle.zip"
unzip sessionmanager-bundle.zip
sudo ./sessionmanager-bundle/install -i /usr/local/sessionmanagerplugin -b /usr/local/bin/session-manager-plugin
./sessionmanager-bundle/install -h
```

jq 설치 
```shell
brew install jq
```

HyperPod Cluster 에 접속
```shell
chmod +x easy-ssh.sh
./easy-ssh.sh -c worker-group-1 hyperpod-cluster-2
```

### HpyerPod 클러스터 환경 설정


Mount S3
```shell
#export BUCKET=사용하고싶은_bucket_name
export BUCKET=sagemaker-us-east-2-529075693336-2

srun -N2 "wget" "https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.deb"
srun -N2 "sudo" "apt-get" "install" "-y"  "./mount-s3.deb"

srun -N2 "sudo" "mkdir" "/home/ubuntu/mnt"
# srun -N2 "sudo" "umount" "/home/ubuntu/mnt"
srun -N2 "sudo" "mount-s3" "--allow-other" "--allow-overwrite" ${BUCKET} "/home/ubuntu/mnt"
```

### LLaMA Factory HyperPod로 복사 
```shell
srun -N2 "cp" "-rf" "/home/ubuntu/mnt/hyperpod/LLaMA-Factory" "LLaMA-Factory"
```

### LLaMA Factory 환경 설치 
```shell
cd /usr/bin/LLaMA-Factory
srun -N2 "rm" "-rf" "../miniconda3"
srun -N2 "rm" "-rf" "Miniconda3-latest*"
srun -N2 "bash" "/home/ubuntu/mnt/hyperpod/LLaMA-Factory/llama_factory_setup.sh"
```

wandb
```shell
export WANDB_API_KEY=사용하고싶은 wandb api key
```

### LLaMA Factory 훈련 시작
```shell
srun -N2 "bash" "/home/ubuntu/mnt/hyperpod/LLaMA-Factory/train_single_lora.sh"
```


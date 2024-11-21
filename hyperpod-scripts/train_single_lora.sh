#!/bin/bash
source  ../miniconda3/bin/activate

conda activate py310

chmod +x ./s5cmd
pip install transformers==4.45.2
pip install tyro==0.8.5
# pip install protobuf==3.20.1

# pip list
cat /home/ubuntu/mnt/hyperpod/LLaMA-Factory/sg_config_qlora.yaml

#download training dataset
./s5cmd sync s3://sagemaker-us-east-2-529075693336-2/dataset-for-training/train/* /home/ubuntu/mnt/hyperpod/LLaMA-Factory/data/

export WANDB_API_KEY=df97535b6e183d5da1d1d01803ea1ac0bd583eb3
#start train
CUDA_VISIBLE_DEVICES=0 llamafactory-cli train /home/ubuntu/mnt/hyperpod/LLaMA-Factory/sg_config_qlora.yaml


./s5cmd sync /home/ubuntu/finetuned_model s3://sagemaker-us-east-2-529075693336-2/hyperpod/llama3-8b-qlora/

#!/bin/bash

# 切换到examples目录
cd "$(dirname "$0")"

# 激活conda环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate open_manus

# 执行Python脚本
python paper_recommend.py

# 执行完成后退出conda环境
conda deactivate 
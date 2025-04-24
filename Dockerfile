FROM python:3.10-slim

WORKDIR /app

# 一次性安装所有系统依赖并清理
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && pip install --upgrade pip wheel \
    && apt-get remove -y build-essential pkg-config \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 使用--no-deps避免重复安装依赖，如果有特定需求可以调整
RUN pip install --no-cache-dir --no-deps -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

LABEL description="优化后的舆情演练基础镜像"
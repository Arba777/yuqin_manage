#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 错误处理函数
handle_error() {
    echo -e "${RED}错误: $1${NC}"
    exit 1
}

echo -e "${YELLOW}开始构建过程...${NC}"

# 1. 拉取 Python 3.11 基础镜像
echo -e "${GREEN}步骤 1: 拉取 Python 3.11 基础镜像${NC}"
docker pull python:3.11-slim || handle_error "拉取基础镜像失败"

# 2. 构建自定义镜像（添加重试机制）
echo -e "${GREEN}步骤 2: 构建自定义镜像${NC}"
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if docker build -t drill_yuqin_base:latest -f Dockerfile .; then
        break
    fi
    retry_count=$((retry_count + 1))
    echo -e "${YELLOW}构建失败，正在进行第 $retry_count 次重试...${NC}"
    sleep 5
done

if [ $retry_count -eq $max_retries ]; then
    handle_error "构建镜像失败，已达到最大重试次数"
fi

# 3. 保存镜像到文件
echo -e "${GREEN}步骤 3: 保存镜像到文件${NC}"
docker save drill_yuqin_base:latest > drill_yuqin_base.tar || handle_error "保存镜像失败"

echo -e "${GREEN}构建完成！${NC}"
echo -e "${YELLOW}使用方法：${NC}"
#echo "1. 将 annotation-system.tar 传输到目标服务器"
echo "2. 在目标服务器上运行：docker load < drill_yuqin_base.tar"
echo "3. 使用 docker-compose up -d 启动服务"

# 4. 清理中间镜像（可选）
echo -e "${YELLOW}是否要清理中间镜像？(y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${GREEN}清理中间镜像...${NC}"
    docker image prune -f
fi

echo -e "${GREEN}所有操作完成！${NC}" 
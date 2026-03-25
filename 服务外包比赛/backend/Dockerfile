# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# 【新增】：配置 HuggingFace 国内镜像源，解决 AutoTokenizer 下载超时的问题
ENV HF_ENDPOINT=https://hf-mirror.com

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        poppler-utils \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev \
        pkg-config \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 【修改】：为 pip install 添加清华大学镜像源，防止 torch 等大体积包下载失败
RUN pip install --no-cache-dir --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ \
    && pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 安装transformers镜像源加速 (由于上方配置了 HF_ENDPOINT，此步骤现在可以顺利连通并下载)
#RUN python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('THUDM/chatglm3-6b', cache_dir='/tmp', trust_remote_code=True)"

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8000

# 定义启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
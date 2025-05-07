FROM python:3.9-slim

WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PORT=5000
ENV CHROMA_PERSIST_DIRECTORY="./knowledge_base"

# 暴露端口
EXPOSE $PORT

# 启动应用
CMD ["python", "backend.py"] 
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（MySQL 客户端库，用于 PyMySQL）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 确保静态文件目录存在（本地开发用，COS模式下空目录即可）
RUN mkdir -p static/products

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

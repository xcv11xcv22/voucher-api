# 使用較精簡的官方 Python image
FROM python:3.11-slim

# 一些常用環境參數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update 

# 先複製 requirements，讓 Docker cache 安裝層
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 對外暴露 API port（gunicorn 用 8000）
EXPOSE 8000

# 使用 gunicorn 啟動，指定工廠模式 create_app()
CMD ["gunicorn", "-w", "1", "--threads", "4", "-b", "0.0.0.0:8000", "app:create_app()"]


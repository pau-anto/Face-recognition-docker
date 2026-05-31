FROM python:3.11-slim
WORKDIR /app

# 1. On installe PyTorch en CPU ONLY d'abord
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.2.1 torchvision==0.17.1
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
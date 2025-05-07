FROM registry.access.redhat.com/ubi9/python-39

# 設定工作目錄
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
FROM python:3.11-slim
WORKDIR /app
# the manifest changes rarely: copy it and install first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# the source changes constantly: copy it last
COPY . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

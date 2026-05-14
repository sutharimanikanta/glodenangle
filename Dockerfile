FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cp .env.example .env 2>/dev/null || true

EXPOSE 8000 8501

CMD uvicorn backend.main:app --host 0.0.0.0 --port 8000 & \
    sleep 3 && \
    streamlit run app.py \
      --server.port 8501 \
      --server.address 0.0.0.0 \
      --browser.gatherUsageStats false

FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Nasiko expects the app to run on port 8000
EXPOSE 8000

# Runtime env vars injected by Nasiko orchestrator
# GATEWAY_URL and GATEWAY_VIRTUAL_KEY set at deploy time — never hardcoded
ENV GATEWAY_URL=http://litellm-gateway:4000
ENV LLM_MODEL=gemini-flash

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

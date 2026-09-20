FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY gradio_ui/ ./gradio_ui/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY .env.example ./.env.example

EXPOSE 8000 7860

CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"]

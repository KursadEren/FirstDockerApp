# ---- Aşama 1: Builder ----
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# ---- Aşama 2: Runtime ----
FROM python:3.11-slim
WORKDIR /app

# Sadece kurulu kütüphaneleri al, build araçlarını değil
COPY --from=builder /root/.local /root/.local

# Kodu kopyala
COPY . .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

ENV PATH=/root/.local/bin:$PATH

CMD ["python", "app.py"]

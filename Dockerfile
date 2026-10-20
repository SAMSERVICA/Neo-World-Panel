FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl unzip ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ARG XRAY_DOWNLOAD=1
RUN if [ "$XRAY_DOWNLOAD" = "1" ]; then \
      ( curl -fsSL --retry 3 --retry-delay 2 -o /tmp/xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip \
        && unzip -o /tmp/xray.zip xray -d /usr/local/bin && chmod +x /usr/local/bin/xray \
        && xray version ) \
      || echo "WARNING: Xray download failed"; \
    fi
COPY . .
ENV KARMA_DATA_DIR=/app/.data
EXPOSE 8000
CMD ["python", "run.py"]

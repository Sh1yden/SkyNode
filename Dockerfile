FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    dos2unix \
    curl \
    ca-certificates \
    iproute2 \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Tuna
RUN curl -sSLf https://get.tuna.am | sh && \
    find /root -name "tuna" -type f -exec mv {} /usr/local/bin/tuna \; 2>/dev/null || true && \
    chmod +x /usr/local/bin/tuna || true

WORKDIR /app

ENV UV_SYSTEM_PYTHON=1
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.1.0
# Важно: обновляем CA сертификаты для HTTPS
RUN update-ca-certificates

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-install-project

COPY . .

RUN chmod +x /usr/local/bin/tuna || true

ENTRYPOINT [ "python", "bot/main.py" ]

FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --system --gid 10001 mitra \
    && useradd --system --uid 10001 --gid mitra --create-home mitra

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip \
    && python -m pip install '.[database]'

USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]
ENTRYPOINT ["mitra-api"]

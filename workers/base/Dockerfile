FROM python:3.11-slim-bookworm

RUN groupadd --system --gid 11000 worker \
    && useradd --system --uid 11000 --gid worker --create-home worker \
    && apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates git tini \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /workspace \
    && chown worker:worker /workspace

COPY entrypoint.sh /usr/local/bin/mitra-worker-entrypoint
USER 11000:11000
WORKDIR /workspace
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/mitra-worker-entrypoint"]

FROM mitra-worker-base:dev
USER root
RUN apt-get update \
    && apt-get install --no-install-recommends -y openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/*
USER 11000:11000

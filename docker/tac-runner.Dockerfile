FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

# Runtime image scaffold only.
# Build/install Codex CLI in a controlled pipeline; do not bake secrets into the image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      git \
      python3 \
      python3-venv \
      nodejs \
      npm \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 tacrunner
USER tacrunner

ENTRYPOINT ["python3"]
CMD ["--version"]

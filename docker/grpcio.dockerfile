FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    unzip \
    make \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Ensure pip and setuptools are present (grpc_tools.protoc imports pkg_resources)
RUN python -m pip install --upgrade pip setuptools

# Install grpc tooling and protobuf (choose versions compatible with Python 3.10)
RUN python -m pip install --no-cache-dir grpcio-tools==1.78.0 protobuf setuptools

WORKDIR /workspace

# Default to an interactive shell; user will mount repo and run `make compile_protos`
CMD ["/bin/bash"]

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
RUN python -m pip install --upgrade pip

# Install grpc tooling and protobuf compatible with protobuf < 3.21.0
# Use an older grpcio-tools build that works with older protobuf runtimes.
RUN python -m pip install --no-cache-dir \
    grpcio-tools==1.44.0 \
    grpcio==1.44.0 \
    "protobuf<3.21.0" \
    mypy-protobuf \
    setuptools

RUN python -c "import pkg_resources; print(pkg_resources.get_distribution('protobuf').version)"

WORKDIR /workspace

# Default to an interactive shell; user will mount repo and run `make compile_protos`
CMD ["/bin/bash"]

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies if necessary (e.g. for pygame)
# PyGame often needs some system libraries
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install pysc2 from PyPI and force compatible protobuf version
# protobuf 4.x+ causes "Descriptors cannot be created directly" error with older generated code
RUN pip install --no-cache-dir pysc2 "protobuf<3.21.0"

# Keep the container running or drop to shell
CMD ["/bin/bash"]

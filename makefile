DOCKER_DIR=docker

GRPC_COMPILLER_IMAGE_NAME=grpcio-compiler
GRPC_COMPILLER_DOCKERFILE_NAME=grpcio.dockerfile

CONVERTER_IMAGE_NAME=pysc2_converter_server
CONVERTER_DOCKERFILE_NAME=Dockerfile

EXPOSED_HOST_PORT=9999
EXPOSED_PORT=9999


.PHONY: build_image
build_image: ## Build the Docker image for the gRPC converter server
	docker build -t $(CONVERTER_IMAGE_NAME) -f $(DOCKER_DIR)/$(CONVERTER_DOCKERFILE_NAME) .

.PHONY: test_docker
test_docker: ## Run pytest inside the dev Docker container
	@make build_image
	docker run --rm -v ".:/workspace" -w /workspace $(CONVERTER_IMAGE_NAME) pytest tests/

.PHONY: run
run: ## Run the gRPC converter server in a Docker container
	@make build_image
	docker run -p $(EXPOSED_HOST_PORT):$(EXPOSED_PORT) --rm -it $(CONVERTER_IMAGE_NAME)



.PHONY: build_grpcio_image
build_grpcio_image: ## Build the Docker image with gRPC tools for compiling .proto files
	docker build -t $(GRPC_COMPILLER_IMAGE_NAME) -f $(DOCKER_DIR)/$(GRPC_COMPILLER_DOCKERFILE_NAME) .

.PHONY: compile_protos
compile_protos: ## Run the Docker container for compiling .proto files
	@make build_grpcio_image
	docker run --rm -it -v ".:/workspace" $(GRPC_COMPILLER_IMAGE_NAME) make compile_protos_python

docker_patch_protos: ## Run the Docker container to patch generated proto files
	@make build_grpcio_image
	docker run --rm -it -v ".:/workspace" $(GRPC_COMPILLER_IMAGE_NAME) make patch_protos_command

.PHONY: init_submodules
init_submodules: ## Initialize and update git submodules
	git submodule update --init --recursive


.PHONY: patch_protos_command
patch_protos_command: ## Patch generated proto files to fix imports
	python ./scripts/patch_protos.py


.PHONY: compile_protos_python
compile_protos_python: ## Generate Python code for the gRPC service from the .proto file
	python -m \
	grpc_tools.protoc \
	-I=./src \
	-I=./src/s2client-proto \
	--python_out=./src \
	--grpc_python_out=./src \
	--mypy_out=./src \
	./src/pysc2_converter_external/proto/service.proto \
	./src/pysc2_converter_external/proto/converter.proto

test: ## Run all tests using pytest
	pytest tests/

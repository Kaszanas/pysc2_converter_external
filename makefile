DOCKER_DIR=docker

.PHONY: build_grpcio_image
build_grpcio_image: ## Build the Docker image with gRPC tools for compiling .proto files
	docker build -t grpcio-compiler -f $(DOCKER_DIR)/grpcio.dockerfile .

.PHONY: compile_protos
compile_protos: ## Run the Docker container for compiling .proto files
	docker run --rm -it -v ".:/workspace" grpcio-compiler make compile_protos_python

.PHONY: init_submodules
init_submodules: ## Initialize and update git submodules
	git submodule update --init --recursive

.PHONY: compile_protos_python
compile_protos_python: ## Generate Python code for the gRPC service from the .proto file
	python -m \
	grpc_tools.protoc \
	-I=./src/proto \
	-I=./src/pysc2 \
	-I=./src/s2client-proto \
	--python_out=./src/pysc2_converter_external/proto \
	--grpc_python_out=./src/pysc2_converter_external/proto \
	./src/proto/service.proto

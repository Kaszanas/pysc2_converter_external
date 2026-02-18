DOCKER_DIR=docker

build_grpcio_image: ## Build the Docker image with gRPC tools for compiling .proto files
	docker build -t grpcio-compiler -f $(DOCKER_DIR)/grpcio.dockerfile .

run_grpcio_container: ## Run the Docker container for compiling .proto files
	docker run --rm -it -v ".:/workspace" grpcio-compiler make compile_protos

compile_protos: ## Generate Python code for the gRPC service from the .proto file
	python -m \
	grpc_tools.protoc \
	-I=./src/proto \
	--python_out=./src/pysc2_converter_external/proto \
	--pyi_out=./src/pysc2_converter_external/proto \
	--grpc_python_out=./src/pysc2_converter_external/proto \
	./src/proto/service.proto

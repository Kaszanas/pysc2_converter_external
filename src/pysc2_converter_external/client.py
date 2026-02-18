import grpc
from pysc2_converter_external.proto import service_pb2_grpc


def main_client(connection_channel: grpc.Channel):

    try:
        stub = service_pb2_grpc.ExternalConverterServiceStub(connection_channel)

        for i in range(1000):
            response = stub.GetRandomNumber(service_pb2_grpc.Empty())
            print(f"index {i} Received random number: {response.random_number}")

    except Exception as e:
        print(f"Failed to create gRPC stub: {e}")
        return


if __name__ == "__main__":
    connection_channel = grpc.insecure_channel("localhost:9999")

    main_client(connection_channel=connection_channel)

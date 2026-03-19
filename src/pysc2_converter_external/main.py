import logging
import time
from concurrent import futures

import grpc

# from pysc2.env.converter.proto import converter_pb2
import pysc2_converter_external.proto.service_pb2_grpc as service_pb2_grpc
from pysc2_converter_external.grpc_service_listener import Listener


def serve():
    logging.info("Attempting to initialize grpc server.")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    listener = Listener()

    # Starting server:
    logging.info("Adding Service to server.")
    service_pb2_grpc.add_ExternalConverterServiceServicer_to_server(
        servicer=listener,
        server=server,
    )

    insecure_port = "[::]:9999"
    logging.info(f"calling server.add_insecure_port({insecure_port}).")
    server.add_insecure_port(insecure_port)
    logging.info("Starting server by calling server.start().")
    server.start()

    # Logging server status:
    try:
        while True:
            logging.info("Server listening")
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Detected KeyboardInterrupt, Stopping server.")
    finally:
        server.stop(grace=10)


def main():

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Initialize the gRPC server and register the converter service implementation
    serve()


if __name__ == "__main__":
    main()

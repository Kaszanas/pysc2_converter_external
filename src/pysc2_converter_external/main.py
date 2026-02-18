from concurrent import futures
import logging
from random import random
import time

import grpc

import pysc2_converter_external.proto.service_pb2_grpc as service_pb2_grpc
import pysc2_converter_external.proto.service_pb2 as service_pb2


class Listener(service_pb2_grpc.ExternalConverterServiceServicer):
    def GetRandomNumber(self, request, context):

        # Example random number

        # get random int between 0 and 100
        random_number = random.randint(0, 100)

        response = service_pb2.RandomNumberResponse(random_number=random_number)

        return response


def serve():
    logging.info("Attempting to initialize grpc server.")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    listener = Listener()

    # Starting server:
    logging.info("Adding Service to server.")
    service_pb2_grpc.add_ExternalConverterServiceServicer_to_server(listener, server)

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
        logging.info("Calling .save_data() on Listener().")
        server.stop(grace=10)


def main():

    # Initialize the gRPC server and register the converter service implementation
    serve()


if __name__ == "__main__":
    print("Hello from pysc2-converter-external!")

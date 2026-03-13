from concurrent import futures
import logging
import time

import grpc

from pysc2_converter_external.grpc_converter import GRPCConverter
import pysc2_converter_external.proto.service_pb2 as service_pb2
import pysc2_converter_external.proto.service_pb2_grpc as service_pb2_grpc
from pysc2.env.converter.proto import converter_pb2


class Listener(service_pb2_grpc.ExternalConverterServiceServicer):
    def ConfigureConverter(
        self,
        request: service_pb2.ConfigureRequest,
        context,
    ) -> service_pb2.ConfigureResponse:

        try:
            self.converter: GRPCConverter = GRPCConverter(
                settings=request.settings,
                environment_info=request.environment_info,
            )
            return service_pb2.ConfigureResponse(success=True)
        except Exception as e:
            logging.error(f"Error occurred while configuring converter: {e}")
            return service_pb2.ConfigureResponse(success=False)

    def GetObservationSpec(self, request, context) -> service_pb2.ObservationSpec:
        observation_spec = self.converter.observation_spec()
        return observation_spec

    def GetActionSpec(self, request, context) -> service_pb2.ActionSpec:
        action_spec = self.converter.action_spec()
        return action_spec

    def ConvertObservation(self, request, context) -> service_pb2.ConvertedObservation:
        converted_obs = self.converter.convert_observation(request)
        return converted_obs

    def ConvertAction(self, request, context) -> converter_pb2.Action:
        converted_action = self.converter.convert_action(request)
        return converted_action


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

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Initialize the gRPC server and register the converter service implementation
    serve()


if __name__ == "__main__":
    main()

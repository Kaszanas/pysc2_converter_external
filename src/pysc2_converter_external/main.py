import logging
import threading
import time
from concurrent import futures

import grpc
from pysc2.env.converter.proto import converter_pb2

import pysc2_converter_external.proto.service_pb2 as service_pb2
import pysc2_converter_external.proto.service_pb2_grpc as service_pb2_grpc
from pysc2_converter_external.grpc_converter import GRPCConverter


class Listener(service_pb2_grpc.ExternalConverterServiceServicer):
    def __init__(self):

        # Map of session_ids to converters, this allows multiple clients to
        # connect to the server and configure their own converters.
        self._converters: dict[int, GRPCConverter] = dict()
        self._max_converter_session_id = 0
        self._lock = threading.Lock()

    def _get_converter(self, session_id: int, context) -> GRPCConverter | None:
        with self._lock:
            converter = self._converters.get(session_id)
        if converter is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND, f"No converter for session {session_id!r}"
            )
        return converter

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
            with self._lock:
                # This makes the session IDs 1-indexed,
                # and reserves session ID 0 to indicate a failed configuration.
                self._max_converter_session_id += 1
                self._converters[self._max_converter_session_id] = self.converter
            return service_pb2.ConfigureResponse(
                success=True,
                session_id=self._max_converter_session_id,
            )
        except Exception as e:
            logging.error(f"Error occurred while configuring converter: {e}")
            # Session ID of 0 is reserved to indicate a failed configuration,
            # session IDs are 1-indexed.
            return service_pb2.ConfigureResponse(success=False, session_id=0)

    def GetObservationSpec(self, request, context) -> service_pb2.ObservationSpec:
        converter = self._get_converter(session_id=request.session_id, context=context)
        observation_spec = converter.observation_spec()
        return observation_spec

    def GetActionSpec(self, request, context) -> service_pb2.ActionSpec:
        converter = self._get_converter(session_id=request.session_id, context=context)
        action_spec = converter.action_spec()
        return action_spec

    def ConvertObservation(
        self,
        request: converter_pb2.Observation,
        context,
    ) -> service_pb2.ConvertedObservation:
        converter = self._get_converter(session_id=request.session_id, context=context)
        converted_obs = converter.convert_observation(observation=request)
        return converted_obs

    def ConvertAction(
        self,
        request: service_pb2.ActionRequest,
        context,
    ) -> converter_pb2.Action:
        converter = self._get_converter(session_id=request.session_id, context=context)
        converted_action = converter.convert_action(action_request=request)
        return converted_action


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

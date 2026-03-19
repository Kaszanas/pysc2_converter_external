import logging
import threading

import grpc

import pysc2_converter_external.proto.converter_pb2 as converter_pb2

# from pysc2.env.converter.proto import converter_pb2
import pysc2_converter_external.proto.service_pb2 as service_pb2
import pysc2_converter_external.proto.service_pb2_grpc as service_pb2_grpc
from pysc2_converter_external.grpc_converter import GRPCConverter


class Listener(service_pb2_grpc.ExternalConverterServiceServicer):
    def __init__(self):

        logging.debug(f"Initializing {self.__class__.__name__}")

        # Map of session_ids to converters, this allows multiple clients to
        # connect to the server and configure their own converters.
        self._converters: dict[int, GRPCConverter] = dict()
        self._max_converter_session_id = 0
        self._lock = threading.Lock()

        logging.debug(f"Finished initializing {self.__class__.__name__}")

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
                logging.debug(
                    f"Successfully configured converter for session {self._max_converter_session_id}"
                )
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
        logging.debug(
            f"Received {self.GetObservationSpec.__name__} request for session {request.session_id}"
        )
        converter = self._get_converter(session_id=request.session_id, context=context)
        observation_spec = converter.observation_spec()

        logging.debug(f"Returning observation spec for session {request.session_id}")

        return observation_spec

    def GetActionSpec(self, request, context) -> service_pb2.ActionSpec:
        logging.debug(
            f"Received GetActionSpec request for session {request.session_id}"
        )

        converter = self._get_converter(session_id=request.session_id, context=context)
        action_spec = converter.action_spec()
        logging.debug(f"Returning action spec for session {request.session_id}")
        return action_spec

    def ConvertObservation(
        self,
        request: converter_pb2.Observation,
        context,
    ) -> service_pb2.ConvertedObservation:
        logging.debug(
            f"Received {self.ConvertObservation.__name__} request for session {request.session_id}"
        )

        converter = self._get_converter(session_id=request.session_id, context=context)
        converted_obs = converter.convert_observation(observation=request)

        logging.debug(
            f"Returning converted observation for session {request.session_id}"
        )

        return converted_obs

    def ConvertAction(
        self,
        request: service_pb2.ActionRequest,
        context,
    ) -> converter_pb2.Action:

        logging.debug(
            f"Received {self.ConvertAction.__name__} request for session {request.session_id}"
        )

        converter = self._get_converter(session_id=request.session_id, context=context)
        converted_action = converter.convert_action(action_request=request)

        logging.debug(f"Returning converted action for session {request.session_id}")

        return converted_action

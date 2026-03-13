from pysc2.env.converter.cc.python import converter
from pysc2.env.converter.proto import converter_pb2

from s2clientprotocol import sc2api_pb2
import pysc2_converter_external.proto.service_pb2 as service_pb2


class GRPCConverter:
    """
    PySC2 environment converter.

    Converts the PySC2 observation/action interface, supporting more standard
    interaction with an ML agent and providing enriched observations.

    Limited configuration is supported through the `ConverterSettings` proto.
    In particular, clients may choose between 'visual' and 'raw' interfaces.
    The visual interface focuses on spatial features and actions which are close
    to those used by a human when playing the game. The raw interface retains
    some spatial features but focuses on numeric unit data; actions being
    specified to units directly, ignoring e.g. the position of the camera.

    The converter maintains some state throughout an episode. This state relies
    on convert_observation and convert_action being called alternately
    throughout the episde. A new converter should be created for each episode.
    """

    def __init__(
        self,
        settings: converter_pb2.ConverterSettings,
        environment_info: converter_pb2.EnvironmentInfo,
    ):
        self._converter = converter.MakeConverter(
            settings=settings.SerializeToString(),
            environment_info=environment_info.SerializeToString(),
        )

    def observation_spec(self) -> service_pb2.ObservationSpec:
        """Returns the observation spec.

        This is a flat mapping of string label to dm_env array spec and varies
        with the specified converter settings and instantiated environment info.
        """

        observation_spec = service_pb2.ObservationSpec()

        for k, v in self._converter.ObservationSpec().items():
            spec = service_pb2.KeyTensorSpec(key=k, spec=v)
            observation_spec.specs.append(spec)

        return observation_spec

    def action_spec(self) -> service_pb2.ActionSpec:
        """Returns the action spec.

        This is a flat mapping of string label to dm_env array spec and varies
        with the specified converter settings and instantiated environment info.
        """

        action_spec = service_pb2.ActionSpec()

        for k, v in self._converter.ActionSpec().items():
            spec = service_pb2.KeyTensorSpec(key=k, spec=v)
            action_spec.specs.append(spec)

        return action_spec

    def convert_observation(
        self, observation: converter_pb2.Observation
    ) -> service_pb2.ConvertedObservation:
        """Converts a SC2 API observation, enriching it with additional info.

        Args:
          observation: Proto containing the SC2 API observation proto for the
            player, and potentially for his opponent. When operating in supervised
            mode must also contain the action taken by the player in response to
            this observation.

        Returns:
          A ConvertedObservation protobuf message.
        """
        serialized_converted_obs = self._converter.ConvertObservation(
            observation.SerializeToString()
        )

        return service_pb2.ConvertedObservation(tensors=serialized_converted_obs)

    def convert_action(
        self, action_request: service_pb2.ActionRequest
    ) -> converter_pb2.Action:
        """Converts an agent action into an SC2 API action proto.

        Note that the returned action also carries the game loop delay requested
        by this player until the next observation.

        Args:
          action_request: ActionRequest protobuf message

        Returns:
          An SC2 API action request + game loop delay.
        """
        converted_action_serialized = self._converter.ConvertAction(
            dict(action_request.tensors)
        )
        converted_action = converter_pb2.Action()
        converted_action.ParseFromString(converted_action_serialized)

        request_action = sc2api_pb2.RequestAction()
        request_action.ParseFromString(
            converted_action.request_action.SerializeToString()
        )
        return converter_pb2.Action(
            request_action=request_action, delay=converted_action.delay
        )

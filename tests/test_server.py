import os
import sys
from pathlib import Path

# Ensure the `src` directory is in the python path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from concurrent import futures

import grpc
import pytest
from pysc2.env.converter.proto import converter_pb2
from s2clientprotocol import common_pb2
from s2clientprotocol import sc2api_pb2 as sc_pb

import pysc2_converter_external.proto.service_pb2 as service_pb2
import pysc2_converter_external.proto.service_pb2_grpc as service_pb2_grpc
from pysc2_converter_external.main import Listener


@pytest.fixture(scope="module")
def grpc_server():
    """Initializes a local test server for the ExternalConverterService."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    listener = Listener()
    service_pb2_grpc.add_ExternalConverterServiceServicer_to_server(listener, server)

    # Bind to an ephemeral port
    port = server.add_insecure_port("[::]:0")
    server.start()

    # Yield the server address for clients
    yield f"localhost:{port}"

    # Teardown
    server.stop(grace=0)


@pytest.fixture(scope="module")
def grpc_client(grpc_server):
    """Creates a client stub mapped to the test server."""
    channel = grpc.insecure_channel(grpc_server)
    stub = service_pb2_grpc.ExternalConverterServiceStub(channel)
    yield stub
    channel.close()


CONVERTER_SETTINGS = converter_pb2.ConverterSettings(
    raw_settings=converter_pb2.ConverterSettings.RawSettings(
        num_unit_features=40,
        max_unit_selection_size=64,
        max_unit_count=512,
        resolution=common_pb2.Size2DI(x=128, y=128),
    ),
    num_action_types=540,
    num_unit_types=217,
    num_upgrade_types=86,
    max_num_upgrades=40,
)

# Reads protobuf data from a file and uses it to create the EnvironmentInfo,
# this is required to configure the converter since it needs the game info to initialize correctly.
EXAMPLE_PROTO_PATH = Path("./tests/test_files/example_game_info.proto").resolve()
with EXAMPLE_PROTO_PATH.open("rb") as f:
    EXAMPLE_GAME_INFO_PROTO = sc_pb.ResponseGameInfo.FromString(f.read())

ENVIRONMENT_INFO = converter_pb2.EnvironmentInfo(game_info=EXAMPLE_GAME_INFO_PROTO)


class TestExternalConverterService:
    @pytest.fixture(scope="class", autouse=True)
    def configure_server_once(self, grpc_client):
        """Configures the server once for all tests in this class."""
        request = service_pb2.ConfigureRequest(
            settings=CONVERTER_SETTINGS,
            environment_info=ENVIRONMENT_INFO,
        )
        response = grpc_client.ConfigureConverter(request)
        # Assuming you want the shared setup to configure correctly
        # assert response.success is True
        assert response.success is True, "Failed to configure converter."

    def test_configure_converter_fail(self, grpc_client):
        """Verifies that the converter configures correctly."""
        settings = converter_pb2.ConverterSettings()
        # Define minimal settings for the converter to not crash when initializing
        settings.visual_settings.screen.x = 64
        settings.visual_settings.screen.y = 64

        env_info = converter_pb2.EnvironmentInfo()

        request = service_pb2.ConfigureRequest(
            settings=CONVERTER_SETTINGS, environment_info=env_info
        )

        response = grpc_client.ConfigureConverter(request)
        assert response.success is False

    def test_get_observation_spec(self, grpc_client):
        """Verifies observation specification is returned."""
        request = service_pb2.Empty()
        response = grpc_client.GetObservationSpec(request)
        # The response should have a repeated 'specs' field
        assert hasattr(response, "specs")

    def test_get_action_spec(self, grpc_client):
        """Verifies action specification is returned."""
        request = service_pb2.Empty()
        response = grpc_client.GetActionSpec(request)
        # The response should have a repeated 'specs' field
        assert hasattr(response, "specs")

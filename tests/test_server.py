import os
import sys

# Ensure the `src` directory is in the python path for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
import grpc
from concurrent import futures

from pysc2_converter_external.main import Listener
import pysc2_converter_external.proto.service_pb2 as service_pb2
import pysc2_converter_external.proto.service_pb2_grpc as service_pb2_grpc

from pysc2.env.converter.proto import converter_pb2


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


class TestExternalConverterService:
    def test_configure_converter(self, grpc_client):
        """Verifies that the converter configures correctly."""
        settings = converter_pb2.ConverterSettings()
        # Define minimal settings for the converter to not crash when initializing
        settings.visual_settings.screen.x = 64
        settings.visual_settings.screen.y = 64

        env_info = converter_pb2.EnvironmentInfo()

        request = service_pb2.ConfigureRequest(
            settings=settings, environment_info=env_info
        )

        response = grpc_client.ConfigureConverter(request)
        assert response.success is True

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

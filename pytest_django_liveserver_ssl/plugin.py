from urllib.parse import urlparse

import pytest
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest

from .fixtures import *  # noqa


@pytest.fixture(autouse=True, scope="function")
def _live_server_ssl_helper(request: FixtureRequest) -> None:
    """Helper to make live_server work, internal to pytest-django.

    This helper will dynamically request the transactional_db fixture
    for a test which uses the live_server fixture.  This allows the
    server and test to access the database without having to mark
    this explicitly which is handy since it is usually required and
    matches the Django behaviour.

    The separate helper is required since live_server can not request
    transactional_db directly since it is session scoped instead of
    function-scoped.

    It will also override settings only for the duration of the test.
    """
    if "live_server_ssl" not in request.fixturenames:
        return

    request.getfixturevalue("transactional_db")

    live_server = request.getfixturevalue("live_server_ssl")
    live_server._live_server_modified_settings.enable()
    request.addfinalizer(live_server._live_server_modified_settings.disable)

    clients = request.getfixturevalue("live_server_ssl_clients_for_patch")
    for c in clients:
        c.defaults["HTTP_HOST"] = urlparse(live_server.remote_url).netloc
        c.defaults["force_https"] = True


def pytest_addoption(parser: Parser) -> None:
    # group = parser.getgroup("live_server_ssl")
    # group.addoption(
    #     "--live-server-host",
    #     action="store",
    #     default="localhost",
    #     type=str,
    #     help="use a host where to listen (default localhost).",
    # )
    # group.addoption(
    #     "--live-server-port",
    #     action="store",
    #     default=0,
    #     type=int,
    #     help="use a fixed port for the live_server fixture.",
    # )
    # parser.addini(
    #     "liveserver_ssl_ca_crt",
    #     "Use own CA cert for sign cert",
    #     default=None,
    # )
    # parser.addini(
    #     "liveserver_ssl_ca_key",
    #     "Use own CA key for sign cert",
    #     default=None,
    # )
    # parser.addini(
    #     "liveserver_ssl_crt",
    #     "Use own CA cert for sign cert",
    #     default=None,
    # )
    # parser.addini(
    #     "liveserver_ssl_key",
    #     "Use own CA key for sign cert",
    #     default=None,
    # )
    parser.addoption("--liveserver-ssl", help="Liveserver addr", default=None)
    parser.addini("liveserver_ssl", "Liveserver addr", default=None)
    parser.addini(
        "liveserver_ssl_scope",
        "modify the scope of the live_server fixture.",
        default="session",
    )

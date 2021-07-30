import os
import shutil
import warnings
from pathlib import Path
from tempfile import mkdtemp
from typing import List, Optional, Type, Generator, cast
from urllib.parse import urlparse

import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from django.test import Client
from pytest_django.lazy_django import skip_if_no_django

from pytest_django_liveserver_ssl._types import Certificate, FixtureScopeType
from pytest_django_liveserver_ssl.helpers import store_file_to_path
from pytest_django_liveserver_ssl.live_server_ssl_helper import HTTPSLiveServer
from pytest_django_liveserver_ssl.ssl_certificate import create_self_signed_cert

__all__ = [
    "live_server_ssl",
    "live_server_ssl_cert",
    "live_server_ssl_ca_cert",
    "live_server_ssl_class",
    "live_server_ssl_clients_for_patch",
]


def _determine_scope(fixture_name: str, config: Config) -> FixtureScopeType:
    return cast(FixtureScopeType, config.getini("liveserver_ssl_scope"))


@pytest.fixture()
def live_server_ssl_clients_for_patch(
    client: Client, admin_client: Client
) -> List[Client]:
    return [client, admin_client]


@pytest.fixture(scope=_determine_scope)
def live_server_ssl_cert() -> Optional[Certificate]:
    return None


@pytest.fixture(scope=_determine_scope)
def live_server_ssl_ca_cert() -> Optional[Certificate]:
    return None


@pytest.fixture(scope=_determine_scope)
def live_server_ssl_class() -> Type[HTTPSLiveServer]:
    return HTTPSLiveServer


@pytest.fixture(scope=_determine_scope)
def live_server_ssl(
    request: FixtureRequest,
    live_server_ssl_cert: Optional[Certificate],
    live_server_ssl_ca_cert: Optional[Certificate],
    live_server_ssl_class: Type[HTTPSLiveServer],
) -> Generator[HTTPSLiveServer, None, None]:
    """Run a live Django server in the background during tests

    The address the server is started from is taken from the
    --liveserver command line option or if this is not provided from
    the DJANGO_LIVE_TEST_SERVER_ADDRESS environment variable.  If
    neither is provided ``localhost:8081,8100-8200`` is used.  See the
    Django documentation for its full syntax.

    NOTE: If the live server needs database access to handle a request
          your test will have to request database access.  Furthermore
          when the tests want to see data added by the live-server (or
          the other way around) transactional database access will be
          needed as data inside a transaction is not shared between
          the live server and test code.

          Static assets will be automatically served when
          ``django.contrib.staticfiles`` is available in INSTALLED_APPS.
    """
    skip_if_no_django()

    import django

    addr = request.config.getvalue("liveserver_ssl") or os.getenv(
        "DJANGO_LIVE_TEST_SERVER_ADDRESS"
    )

    if addr and ":" in addr:
        if django.VERSION >= (1, 11):
            ports = addr.split(":")[1]
            if "-" in ports or "," in ports:
                warnings.warn(
                    "Specifying multiple live server ports is not supported "
                    "in Django 1.11. This will be an error in a future "
                    "pytest-django release."
                )

    if not addr:
        if django.VERSION < (1, 11):
            addr = "0.0.0.0:8081,8100-8200"
        else:
            addr = "0.0.0.0"

    certificate_file = None
    key_file = None
    ca_cert = None
    ca_key = None
    if live_server_ssl_cert:
        certificate_file = live_server_ssl_cert["crt"]
        key_file = live_server_ssl_cert["key"]

    if live_server_ssl_ca_cert:
        ca_cert = live_server_ssl_ca_cert["crt"]
        ca_key = live_server_ssl_ca_cert["key"]

    tmp_root = mkdtemp()
    if not certificate_file or not key_file:
        certificate_file = os.path.join(tmp_root, "localhost.crt")
        key_file = os.path.join(tmp_root, "localhost.key")

    if not isinstance(certificate_file, (str, Path)):
        certificate_file = store_file_to_path(certificate_file, tmp_root)
    if not isinstance(key_file, (str, Path)):
        key_file = store_file_to_path(key_file, tmp_root)

    if not os.path.exists(certificate_file) or not os.path.exists(key_file):
        create_self_signed_cert(
            key_file,
            certificate_file,
            ca_root_crt=ca_cert,
            ca_root_key=ca_key,
            domain="localhost",
        )

    server = live_server_ssl_class(
        addr, key_file=key_file, certificate_file=certificate_file
    )
    request.addfinalizer(server.stop)

    live_server_url = urlparse(server.url)

    remote_url = f"https://localhost:{live_server_url.port}"
    server.__dict__["url"] = remote_url
    server.__dict__["remote_url"] = remote_url
    server.__dict__["port"] = live_server_url.port
    yield server

    if tmp_root:
        shutil.rmtree(tmp_root)

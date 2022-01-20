# TODO move to application
import ssl
from distutils.version import LooseVersion
from typing import Type, Union, Tuple, Any, Dict

from django import get_version
from django.core.servers.basehttp import ThreadedWSGIServer
from django.core.servers.basehttp import WSGIRequestHandler as _WSGIRequestHandler
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler
from pytest_django.live_server_helper import LiveServer

from pytest_django_liveserver_ssl._types import PathType

if LooseVersion(get_version()) >= LooseVersion("1.5"):
    pass
else:
    upath = str


class SecureHTTPServer(ThreadedWSGIServer):
    def __init__(
        self,
        address: Tuple[str, Union[str, int]],
        handler_cls: Type[_WSGIRequestHandler],
        certificate: str,
        key: str,
        **kwargs: Any
    ):
        super(SecureHTTPServer, self).__init__(address, handler_cls, **kwargs)
        self.socket = ssl.wrap_socket(
            self.socket,
            certfile=certificate,
            keyfile=key,
            server_side=True,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            cert_reqs=ssl.CERT_NONE,
        )


class WSGIRequestHandler(QuietWSGIRequestHandler):
    def get_environ(self) -> Dict[str, Any]:
        env = super(WSGIRequestHandler, self).get_environ()
        env["HTTPS"] = "on"
        return env


class HTTPSLiveServerThread(LiveServerThread):
    def __init__(self, *args: Any, **kwargs: Any):
        self.certificate_file = kwargs.pop("certificate_file", None)
        self.key_file = kwargs.pop("key_file", None)
        self.domain = kwargs.pop("domain", "localhost")
        super().__init__(*args, **kwargs)

    def _create_server(self) -> SecureHTTPServer:
        return SecureHTTPServer(
            (self.host, self.port),
            WSGIRequestHandler,
            allow_reuse_address=False,
            certificate=self.certificate_file,
            key=self.key_file,
        )


class HTTPSLiveServer(LiveServer):
    """The liveserver fixture

    This is the object which is returned to the actual user when they
    request the ``live_server`` fixture.  The fixture handles creation
    and stopping however.
    """

    remote_url: str

    def __init__(self, addr: str, certificate_file: PathType, key_file: PathType):
        from django.db import connections
        super().__init__(addr)
        self.stop()
        import django
        from django.test.utils import modify_settings

        live_server_kwargs = dict(
            connections_override=self.thread.connections_override,
            static_handler=self.thread.static_handler,
            certificate_file=certificate_file,
            key_file=key_file,
        )

        if django.VERSION < (1, 11):
            from pytest_django.live_server_helper import parse_addr  # type: ignore

            host, possible_ports = parse_addr(addr)
            self.thread = HTTPSLiveServerThread(
                host, possible_ports, **live_server_kwargs
            )
        else:
            port: Union[str, int]
            try:
                host, port = addr.split(":")
            except ValueError:
                host = addr
                port = 0
            self.thread = HTTPSLiveServerThread(
                host, port=int(port), **live_server_kwargs
            )

            connections_override = {}
            for conn in connections.all():
                # If using in-memory sqlite databases, pass the connections to
                # the server thread.
                if conn.vendor == "sqlite" and conn.is_in_memory_db():  # type: ignore
                    # Explicitly enable thread-shareability for this connection.
                    conn.inc_thread_sharing()  # type: ignore
                    connections_override[conn.alias] = conn

        self._live_server_modified_settings = modify_settings(
            ALLOWED_HOSTS={"append": host}
        )
        self.thread.daemon = True
        self.thread.start()
        self.thread.is_ready.wait()

        if self.thread.error:
            raise self.thread.error

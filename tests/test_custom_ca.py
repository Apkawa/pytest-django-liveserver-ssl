from pathlib import Path

CERT_ROOT = Path(__file__).parent / Path("certs/")
CA_CERT_FILE = CERT_ROOT / Path("RootCA.crt")
CA_KEY_FILE = CERT_ROOT / Path("RootCA.key")


def test_custom_ca(django_testdir):
    django_testdir.create_test_module(
        f"""
        from pathlib import Path

        import pytest
        import requests
        from OpenSSL import crypto

        from pytest_django_liveserver_ssl._types import Certificate

        CA_CERT_FILE = "{CA_CERT_FILE}"
        CA_KEY_FILE = "{CA_KEY_FILE}"

        @pytest.fixture(scope="session")
        def live_server_ssl_ca_cert() -> Certificate:
            return dict(crt=CA_CERT_FILE, key=CA_KEY_FILE)

        def test_custom_ca(live_server_ssl):
            assert live_server_ssl.thread.certificate_file.startswith("/tmp/")
            assert live_server_ssl.thread.key_file.startswith("/tmp/")

            r = requests.get(live_server_ssl.remote_url, verify=False)
            assert r.text == "OK"

            cert = crypto.load_certificate(
                crypto.FILETYPE_PEM, open(live_server_ssl.thread.certificate_file, "rb").read()
            )
            assert cert.get_issuer().CN == "Example-Root-CA"
        """
    )
    result = django_testdir.runpytest_subprocess("--tb=short", "-v")
    result.stdout.fnmatch_lines(["*test_custom_ca*PASSED*"])
    assert result.ret == 0

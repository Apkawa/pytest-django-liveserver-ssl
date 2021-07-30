from pathlib import Path

CERT_ROOT = Path(__file__).parent / Path("certs/")
CERT_FILE = CERT_ROOT / Path("localhost.crt")
KEY_FILE = CERT_ROOT / Path("localhost.key")


def test_custom_cert(django_testdir):
    django_testdir.create_test_module(
        f"""
        from pathlib import Path

        import pytest
        import requests

        from pytest_django_liveserver_ssl._types import Certificate

        CERT_FILE = "{CERT_FILE}"
        KEY_FILE = "{KEY_FILE}"


        @pytest.fixture(scope="session")
        def live_server_ssl_cert() -> Certificate:
            return dict(crt=CERT_FILE, key=KEY_FILE)


        def test_custom_cert(live_server_ssl):
            assert live_server_ssl.thread.certificate_file == CERT_FILE
            assert live_server_ssl.thread.key_file == KEY_FILE

            r = requests.get(live_server_ssl.remote_url, verify=False)
            assert r.text == "OK"
        """
    )
    result = django_testdir.runpytest_subprocess("--tb=short", "-v")
    result.stdout.fnmatch_lines(["*test_custom_cert*PASSED*"])
    assert result.ret == 0

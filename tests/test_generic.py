import requests

from tests.app.models import ExampleModel


def test_fixture(live_server_ssl):
    assert live_server_ssl
    assert live_server_ssl.remote_url.startswith("https://localhost:")
    assert live_server_ssl.url.startswith("http://0.0.0.0:")
    assert live_server_ssl.thread.host == "0.0.0.0"
    assert str(live_server_ssl.thread.certificate_file).startswith("/tmp")
    assert str(live_server_ssl.thread.key_file).startswith("/tmp")


def test_django(client):
    res = client.get("/")
    assert res.content == b"OK"


def test_live_server_connection(live_server_ssl):
    response = requests.get(live_server_ssl.remote_url, verify=False)
    assert response.text == "OK"


def test_transaction_shares(live_server_ssl):
    m = ExampleModel(name="foo")
    m.save()

    response = requests.get(live_server_ssl.remote_url + f"/test/{m.pk}/", verify=False)
    assert response.text == "foo"

    m.name = "bar"
    m.save()

    response = requests.get(live_server_ssl.remote_url + f"/test/{m.pk}/", verify=False)
    assert response.text == "bar"

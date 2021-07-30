import tempfile
from pathlib import Path

from OpenSSL import crypto

from pytest_django_liveserver_ssl.ssl_certificate import create_self_signed_cert


def test_ssl_certificate_without_ca():
    cert_file = tempfile.NamedTemporaryFile(suffix=".crt")
    key_file = tempfile.NamedTemporaryFile(suffix=".key")

    create_self_signed_cert(cert_file=cert_file.name, key_file=key_file.name)

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())

    assert cert.get_subject().CN == "localhost"


def test_ssl_certificate_with_root_ca():
    ca_cert_file = tempfile.NamedTemporaryFile(suffix=".crt")
    ca_key_file = tempfile.NamedTemporaryFile(suffix=".key")

    create_self_signed_cert(
        cert_file=ca_cert_file.name,
        key_file=ca_key_file.name,
        domain="example.com",
        fields=dict(OU="Example company LTD", emailAddress=None),
    )

    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_file.read())
    assert ca_cert.get_subject().CN == "example.com"
    assert ca_cert.get_subject().OU == "Example company LTD"

    cert_file = tempfile.NamedTemporaryFile(suffix=".crt")
    key_file = tempfile.NamedTemporaryFile(suffix=".key")

    create_self_signed_cert(
        cert_file=cert_file.name,
        key_file=key_file.name,
        ca_root_crt=ca_cert_file.name,
        ca_root_key=ca_key_file.name,
    )

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())

    assert cert.get_subject().CN == "localhost"
    assert cert.get_issuer().CN == "example.com"


CERT_ROOT = Path(__file__).parent / Path("certs/")
CA_CERT_FILE = CERT_ROOT / Path("RootCA.crt")
CA_KEY_FILE = CERT_ROOT / Path("RootCA.key")


def test_ssl_certificate_with_exists_ca():
    ca_cert_file = CA_CERT_FILE
    ca_key_file = CA_KEY_FILE

    ca_cert = crypto.load_certificate(
        crypto.FILETYPE_PEM, open(ca_cert_file, "rb").read()
    )
    assert ca_cert.get_subject().CN == "Example-Root-CA"

    cert_file = tempfile.NamedTemporaryFile(suffix=".crt")
    key_file = tempfile.NamedTemporaryFile(suffix=".key")

    create_self_signed_cert(
        cert_file=cert_file.name,
        key_file=key_file.name,
        ca_root_crt=ca_cert_file,
        ca_root_key=ca_key_file,
    )

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())

    assert cert.get_subject().CN == "localhost"
    assert cert.get_issuer().CN == "Example-Root-CA"

    # Emulate add cert to trusted
    store = crypto.X509Store()
    store.add_cert(ca_cert)

    ctx = crypto.X509StoreContext(store, cert)
    ctx.verify_certificate()

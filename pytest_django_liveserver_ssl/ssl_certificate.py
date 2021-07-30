from pathlib import Path
from typing import Optional, Dict

from OpenSSL import crypto

from pytest_django_liveserver_ssl._types import FileOrPath, TypedDict


class FieldsType(TypedDict):
    C: str
    ST: str
    L: str
    O: str
    OU: str
    emailAddress: str


def create_self_signed_cert(
    key_file: FileOrPath,
    cert_file: FileOrPath,
    domain: Optional[str] = None,
    fields: Optional[Dict[str, str]] = None,
    ca_root_key: Optional[FileOrPath] = None,
    ca_root_crt: Optional[FileOrPath] = None,
    hash_alg: str = "sha256",
) -> None:
    """
    """
    if not domain:
        domain = "localhost"

    _fields = dict(
        CN=domain,
        C="US",
        ST="Minnesota",
        L="Minnetonka",
        O="my company",
        OU="my organization",
        emailAddress="test@example.com",
    )
    _fields.update(fields or {})

    # create a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    cert_req = None
    if ca_root_key and ca_root_crt:
        if isinstance(ca_root_key, (str, Path)):
            ca_root_key = open(ca_root_key, "rb")
        if isinstance(ca_root_crt, (str, Path)):
            ca_root_crt = open(ca_root_crt, "rb")
        ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, ca_root_key.read())
        ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_root_crt.read())

        cert_req = crypto.X509Req()

        ca_cert_subj = ca_cert.get_subject()
        cert_req_subj = cert_req.get_subject()
        for k in ["ST", "L", "O", "OU", "emailAddress"]:
            v = getattr(ca_cert_subj, k)
            if v:
                setattr(cert_req_subj, k, v)
        cert_req_subj.CN = domain
        # TODO alt names
        cert_req.set_pubkey(key)
        cert_req.sign(ca_key, hash_alg)

    # create a self-signed cert
    cert = crypto.X509()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)

    # https://letsencrypt.org/ru/docs/certificates-for-localhost/
    # extensions = [
    #     crypto.X509Extension(b'basicConstraints', False, b'CA:FALSE'),
    #     crypto.X509Extension(b'keyUsage', True, 'digitalSignature, nonRepudiation'),
    #     crypto.X509Extension(b'extendedKeyUsage', True, b'serverAuth'),
    #     crypto.X509Extension(b'subjectAltName', False, b'DNS:www.ex.com,IP:1.2.3.4')
    # ]
    # cert.add_extensions(extensions)

    if cert_req:
        cert.set_issuer(ca_cert.get_subject())

        cert.set_subject(cert_req.get_subject())
        cert.set_pubkey(cert_req.get_pubkey())
        cert.sign(ca_key, hash_alg)
    else:
        subj = cert.get_subject()
        for name, value in _fields.items():
            if value:
                setattr(subj, name, value)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, hash_alg)

    if isinstance(cert_file, (str, Path)):
        cert_file = open(cert_file, "wb")
    if isinstance(key_file, (str, Path)):
        key_file = open(key_file, "wb")

    cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    cert_file.flush()
    key_file.flush()

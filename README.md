[![Documentation Status](https://readthedocs.org/projects/pytest-django-liveserver-ssl/badge/?version=latest)](https://pytest-django-liveserver-ssl.readthedocs.io/en/latest/?badge=latest)

[![ci](https://github.com/Apkawa/pytest-django-liveserver-ssl/actions/workflows/ci.yml/badge.svg)](https://github.com/Apkawa/pytest-django-liveserver-ssl/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/Apkawa/pytest-django-liveserver-ssl/branch/master/graph/badge.svg)](https://codecov.io/gh/Apkawa/pytest-django-liveserver-ssl) </br>

[![PyPi](https://img.shields.io/pypi/v/pytest-django-liveserver-ssl.svg)](https://pypi.python.org/pypi/pytest-django-liveserver-ssl)
[![PyPi Python versions](https://img.shields.io/pypi/pyversions/pytest-django-liveserver-ssl.svg)](https://pypi.python.org/pypi/pytest-django-liveserver-ssl)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)</br>

# pytest-django-liveserver-ssl

Add `live_server_ssl` fixture for pytest-django.

# Installation

```bash
pip install pytest-django-liveserver-ssl
```

or from git

```bash
pip install -e git+https://githib.com/Apkawa/pytest-django-liveserver-ssl.git@master#egg=pytest-django-liveserver-ssl
```

# Usage

```python
import requests


def test_live_server_connection(live_server_ssl):
    assert live_server_ssl.remote_url.startswith("https://localhost:")
    assert live_server_ssl.url.startswith("http://0.0.0.0:")

    response = requests.get(live_server_ssl.remote_url, verify=False)
    assert response.text == "OK"
```

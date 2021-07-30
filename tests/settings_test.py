# coding: utf-8
from __future__ import unicode_literals

from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # Oops, not working
        # https://github.com/pytest-dev/pytest-django/issues/783
        "NAME": ":memory:",
    }
}

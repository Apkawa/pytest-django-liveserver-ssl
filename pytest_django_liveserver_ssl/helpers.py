import os
import shutil
from tempfile import mktemp, mkdtemp
from typing import BinaryIO, Optional

from pytest_django_liveserver_ssl._types import PathType


def store_file_to_path(file: BinaryIO, path: Optional[PathType] = None) -> str:
    t = path or mkdtemp()
    if os.path.isdir(t):
        t = mktemp(suffix=".crt", dir=t)

    with open(t, "wb") as f:
        shutil.copyfileobj(file, f)
    return str(t)

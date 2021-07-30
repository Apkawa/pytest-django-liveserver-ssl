from pathlib import Path
from typing import Union, BinaryIO, TYPE_CHECKING

from typing_extensions import TypedDict

PathType = Union[str, Path]
FileOrPath = Union[BinaryIO, PathType]


class Certificate(TypedDict):
    crt: FileOrPath
    key: FileOrPath


if TYPE_CHECKING:
    from _pytest.fixtures import _Scope as FixtureScopeType  # noqa
else:
    FixtureScopeType = str

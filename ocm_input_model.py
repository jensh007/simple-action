import dataclasses
import typing
import gci.componentmodel as cm
from dataclasses import dataclass
from typing import Optional, Any


@dataclass(frozen=True)
class FileInput:
    content_type: str
    name: str


@dataclass(frozen=True)
class LabelInput:
    position: Optional[str]
    name: str
    value: Optional[Any]


@dataclass(frozen=True)
class OcmInput:
    name: str
    version: str
    provider: str
    images: Optional[list[str]]
    helm_charts: Optional[list[str]]
    files: Optional[list[FileInput]]
    labels: Optional[list[LabelInput]]
    references: Optional[list[cm.ComponentIdentity]]
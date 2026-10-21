# encoding: utf-8
"""
"""

from typing import Any, TypeVar, Type

from abc import ABCMeta as _ABCMeta
from dataclasses import asdict, fields

_T = TypeVar('T')


class FrontendSharedDataclassABC(metaclass=_ABCMeta):
    """
    Base class for dataclasses whose instances could be initialized
    with extra garbage fields (probably coming from frontend).

    The ``@dataclass`` decorator still need to be used on concrete dataclasses.
    """

    @classmethod
    def _class_field_names(cls) -> frozenset[str]:
        try:
            return cls.__cached_class_field_names
        except AttributeError:
            names = frozenset(f.name for f in fields(cls))
            cls.__cached_class_field_names = names
            return names

    @classmethod
    def unsafe_init(cls: Type[_T], **kwargs) -> _T:
        """
        Class method: init the dataclass instance with possible extra garbage fields in arguments,
        which will just be ignored.
        """
        valid_names = cls._class_field_names()
        valid_kwargs = {k: v for k, v in kwargs.items() if k in valid_names}
        return cls(**valid_kwargs)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

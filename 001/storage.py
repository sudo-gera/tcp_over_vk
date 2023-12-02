from __future__ import annotations
import pathlib
import os.path
import json
import typing

class Storage:
    def __init__(self, file: typing.Any, _path: str = '', _safe: bool = False):
        self.__file = file
        self.__path = _path
        try:
            file.__aexit__
        except Exception:
            _safe = True
        self.__safe = _safe
    
    def __getattr__(self, name: str) -> Storage:
        return Storage(self.__file, self.__path + '.' + name, self.__safe)
    
    def __getitem__(self, key: typing.Any) -> Storage:
        return self.__getattr__(json.dumps(key))

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        return self.__setattr__(json.dumps(key), value)

    def __delitem__(self, key: typing.Any) -> None:
        return self.__delattr__(json.dumps(key))

    def __call__(self, *a: typing.Any, remove: bool = False, default: typing.Any = ...) -> typing.Any:
        if a:
            assert len(a) == 1
            if not self.__safe:
                raise TypeError
            self.__file[self.__path] = a[0]
        else:
            if remove:
                if not self.__safe:
                    raise TypeError
                del self.__file[self.__path]
            elif default is ... or self.__path in self.__file:
                return self.__file[self.__path]
            else:
                return default

    def __bool__(self) -> bool:
        return self.__path in self.__file

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if name.startswith(f'_{self.__class__.__name__}'):
            return super().__setattr__(name, value)
        getattr(self, name)(value)

    def __delattr__(self, name: str) -> None:
        if name.startswith(f'_{self.__class__.__name__}'):
            return super().__delattr__(name)
        getattr(self, name)(remove = 1)

    async def __aenter__(self) -> Storage:
        return Storage(self.__file, self.__path, True)

    async def __aexit__(self, *a: typing.Any) -> None:
        await self.__file()


import pathlib
import os.path
import asyncio
import json
import re
import typing
import os

from annotation import eat

def _opener(path: eat | str | bytes | os.PathLike[str] | os.PathLike[bytes], flags: int) -> int:
    return os.open(path, flags, mode=0o600)

def list_groups() -> list[str]:
    res = [
        q.groups()[0]
        for q in [
            re.fullmatch(r'\.tcp_over_vk_(\d+)\.json', q)
            for q in os.listdir(pathlib.Path().home())
        ]
        if q is not None
    ]
    return res

class file:
    def __init__(self, group_id: eat | int|str|None = None):
        suff = f'_{group_id}' if group_id is not None else ''
        self.path = os.path.join(pathlib.Path().home(), f'.tcp_over_vk{suff}.json')
        data = ''
        try:
            with open(self.path, 'r', opener=_opener) as file:
                data = file.read()
                self.db = json.loads(data)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            if not data.strip():
                self.db = {}
            else:
                raise

    def __getitem__(self, key: str) -> typing.Any:
        return self.db[key]

    def __setitem__(self, key: str, value: typing.Any) -> None:
        self.db[key] = value
        with open(self.path, 'w', opener=_opener) as file:
            json.dump(self.db, file, indent=4)

    def __delitem__(self, key: str) -> None:
        del self.db[key]
        with open(self.path, 'w', opener=_opener) as file:
            json.dump(self.db, file, indent=4)

    def __contains__(self, key: str) -> bool:
        return key in self.db

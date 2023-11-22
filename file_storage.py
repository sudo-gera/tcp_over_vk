import pathlib
import os.path
import json
from typing import Any

def file(group_id, data = None):
    path = os.path.join(pathlib.Path().home(), f'.tcp_over_vk_{group_id}.json')

    def opener(path, flags):
        return os.open(path, flags, mode=0o600)

    def get_file():
        try:
            with open(path, 'r', opener=opener) as file:
                return json.load(file)
        except Exception:
            return {}

    def set_file(data):
        with open(path, 'w', opener=opener) as file:
            return json.dump(data, file)
    
    if data is None:
        return get_file()
    return set_file(data)

class Storage:
    def __init__(self, group_id, path = ''):
        self.__path = path
        self.__group_id = group_id

    def __getattr__(self, name):
        new_path = self.__path + '.' + name
        data = file(self.__group_id)
        if new_path in data:
            return data[new_path]
        return Storage(self.__group_id, new_path)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            return super().__setattr__(name, value)
        new_path = self.__path + '.' + name
        data = file(self.__group_id)
        data[new_path] = value
        file(self.__group_id, data)
    
    def __delattr__(self, name: str, value: Any) -> None:
        new_path = self.__path + '.' + name
        data = file(self.__group_id)
        del data[new_path]
        file(self.__group_id, data)
    
    def __getitem__(self, key):
        return self.__getattr__(json.dumps(key))
    
    def __setitem__(self, key, value):
        return self.__setattr__(json.dumps(key), value)

    def __delitem__(self, key):
        return self.__delattr__(json.dumps(key))
    

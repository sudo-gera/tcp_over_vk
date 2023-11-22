import pathlib
import os.path
import json
from typing import Any

path = os.path.join(pathlib.Path().home(), '.tcp_over_vk.json')

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
    

class Storage:
    def __init__(self, path = ''):
        self.__path = path

    def __getattr__(self, name):
        new_path = self.__path + '.' + name
        data = get_file()
        if new_path in data:
            return data[new_path]
        return Storage(new_path)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            self.__dict__[name] = value
            return
        new_path = self.__path + '.' + name
        data = get_file()
        data[new_path] = value
        set_file(data)
    
    def __delattr__(self, name: str, value: Any) -> None:
        new_path = self.__path + '.' + name
        data = get_file()
        del data[new_path]
        set_file(data)
    
    def __getitem__(self, key):
        return self.__getattr__(json.dumps(key))
    
    def __setitem__(self, key, value):
        return self.__setattr__(json.dumps(key), value)

    def __delitem__(self, key):
        return self.__delattr__(json.dumps(key))
    
storage = Storage()

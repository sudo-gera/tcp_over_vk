import pathlib
import os.path
import json

import file

class Storage:
    def __init__(self, group_id, _path = ''):
        self.__group_id = group_id
        self.__path = _path
        self.__file = file.file(group_id)
    
    def __getattr__(self, name: str):
        return Storage(self.__group_id, self.__path + '.' + name)
    
    def __getitem__(self, key):
        return self.__getattr__(json.dumps(key))

    def __call__(self, *a):
        if a:
            assert len(a) == 1
            self.__file[self.__path] = a[0]
        else:
            return self.__file[self.__path]

    def __bool__(self):
        return self.__path in self.__file


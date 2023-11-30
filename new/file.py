import pathlib
import os.path
import asyncio
import json

def _opener(path, flags):
    return os.open(path, flags, mode=0o600)

class file:
    def __init__(self, group_id):
        self.group_id = group_id
        self.path = os.path.join(pathlib.Path().home(), f'.tcp_over_vk_{group_id}.json')
        try:
            with open(self.path, 'r', opener=_opener) as file:
                self.db = json.load(file)
        except FileNotFoundError:
            self.db = {}

    def __getitem__(self, key):
        return self.db[key]

    def __setitem__(self, key, value):
        self.db[key] = value
        with open(self.path, 'w', opener=_opener) as file:
            json.dump(self.db, file, indent=4)

    def __contains__(self, key):
        return key in self.db
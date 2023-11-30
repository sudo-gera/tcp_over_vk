import os
import sys

class tmp_file:
    def __init__(self, group_id: str|int):
        if sys.platform == 'darwin':
            TMP_DIR = '/private/tmp/'
        elif os.getcwd().startswith('/data/data/com.termux'):
            TMP_DIR = '/data/data/com.termux/files/usr/var/run'
        else:
            TMP_DIR = '/tmp/'

        self.prefix = os.path.join(TMP_DIR, f'tcp_over_vk_{os.getuid()}_{group_id}_')

    def __getattr__(self, name):
        return self.prefix + name + '.' + name

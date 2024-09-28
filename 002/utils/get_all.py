from pathlib import Path
from os import listdir
from operator import itemgetter, methodcaller

def get_all(cur_file: str) -> list[str]:
    return list(
        {
            *map(
                itemgetter(
                    slice(None, -3)
                ),
                filter(
                    methodcaller('endswith', '.py'),
                    listdir(
                        Path(cur_file).resolve().parent
                    ),
                ),
            )
        } - {'__init__'}
    )

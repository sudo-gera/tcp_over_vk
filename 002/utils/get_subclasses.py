from typing import TypeVar

T = TypeVar('T')

def get_subclasses(root: type[T]) -> set[type[T]]:
    whole_subclass_tree : set[type[T]] = set()
    queue : list[type[T]] = [root]
    for cls in queue:
        if cls in whole_subclass_tree:
            continue
        whole_subclass_tree.add(cls)
        queue.extend(cls.__subclasses__())
    return whole_subclass_tree - {root}

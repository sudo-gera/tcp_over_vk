import sys
if sys.version_info.minor >= 10:
    class eat:
        pass
else:
    class eater:
        def __or__(self, oth):
            return self
    eat = eater()
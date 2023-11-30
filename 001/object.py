class Object(dict):  # allow a.name instead of a['name'] for JSON types
    def __init__(self, *a, **s):
        super().__init__(*a, **s)
        self.__dict__ = self

def _convert(obj, build, Obj):
    if isinstance(obj, dict):
        return Obj({q: build(obj[q]) for q in obj})
    if isinstance(obj, list):
        return [build(w) for w in obj]
    return obj

def build(obj):
    return _convert(obj, build, Object)

def destroy(obj):
    return _convert(obj, destroy, lambda x:x)

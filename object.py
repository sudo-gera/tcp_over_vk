class Object(dict):  # allow a.name instead of a['name'] for JSON types
    def __init__(self, *a, **s):
        super().__init__(*a, **s)
        self.__dict__ = self

    @staticmethod
    def __convert(obj, build, Obj):
        if isinstance(obj, dict):
            return Obj({q: build(w) for q,w in obj.items()})
        if isinstance(obj, list):
            return [build(w) for w in obj]
        return obj

    @staticmethod
    def _build(obj):
        return Object.__convert(obj, Object._build, Object)

    @staticmethod
    def _destroy(obj):
        return Object.__convert(obj, Object._destroy, lambda x:x)

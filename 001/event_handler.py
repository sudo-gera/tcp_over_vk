event_handlers = {}

class handle:
    def __init__(self, event_name):
        self.event_name = event_name
    
    def __call__(self, func):
        assert self.event_name not in event_handlers
        event_handlers[self.event_name] = func
        return func


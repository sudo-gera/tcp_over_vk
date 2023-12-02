import secrets
import time
def make_id() -> int:
    return secrets.randbelow(2**64) + time.time_ns() * 2**64

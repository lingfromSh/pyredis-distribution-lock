import time
from threading import current_thread
from functools import wraps


SUCCESS = 1
FAILURE = -1


def release_lock(rclient, lock_name: str) -> bool:
    """
    Releases a lock.

    :param      rclient:    The rclient
    :param      lock_name:  The lock name
    """
    return rclient.delete(lock_name) == SUCCESS


def acquire_lock(rclient, lock_name: str, timeout: int, acquire_time: int):
    """
    Acquire a lock.

    :param      func:  The function
    """

    t_id = current_thread().ident

    def wrapper(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            end = time.time() + timeout
            while time.time() < end:
                if rclient.setnx(lock_name, t_id) == SUCCESS:
                    rclient.expire(lock_name, acquire_time)
                    ret = func(*args, **kwargs)
                    release_lock(rclient, lock_name)
                    return ret, True
                elif rclient.ttl(lock_name) == FAILURE:
                    rclient.expire(lock_name, timeout)

            return (args, kwargs), False

        return _wrapper

    return wrapper

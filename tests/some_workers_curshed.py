import random
import random
import redis
import time
from concurrent.futures import ThreadPoolExecutor
from lock import RedisDistributionLock

r = redis.Redis('localhost', port=6379, db=0)
lock = RedisDistributionLock('balance-lock', r)

# account key
BALANCE = "balance"


def incr_balance():
    if lock.acquire(acquire_time=1):
        balance = int(r.get(BALANCE).decode())
        raise RuntimeError("Crushed")
        r.set(BALANCE, balance + 1)
        lock.release()


def decr_balance():
    if lock.acquire(acquire_time=1):
        balance = int(r.get(BALANCE).decode())
        r.set(BALANCE, balance - 1)
        lock.release()


def done_callbak(f):
    try:
        return f.result()
    except Exception:
        pass


def test_lock():
    executor = ThreadPoolExecutor(4)

    # init balance
    r.set(BALANCE, 0)

    change_handles = {'incr': incr_balance, 'decr': decr_balance}
    changes = [list(change_handles.keys())[random.randint(0, 1)] for i in range(5)]
    for change in changes:
        f = executor.submit(change_handles[change])
        f.add_done_callback(done_callbak)

    executor.shutdown()
    balance = int(r.get(BALANCE).decode())
    assert balance == sum(map(lambda x: 0 if x == 'incr' else -1, changes)), "Wrong"
    print("Passed!!!")


if __name__ == "__main__":
    test_lock()

import random
import redis
import time
from lock import acquire_lock

redis = redis.Redis(host='localhost', port=6379, db=0)

# 账户
BALANCE = "balance"

# 初始化账户
redis.set(BALANCE, 0)

# 分布式锁
BALANCE_REDIS_LOCK = "balance-lock"

# 超时/获取锁时长
TIMEOUT = 5
MAX_ACQUIRE_TIME = 1


@acquire_lock(redis, BALANCE_REDIS_LOCK, TIMEOUT, MAX_ACQUIRE_TIME)
def increase_balance(count):
    """
    Increases balance.

    :param      count:  要添加的金额
    """
    balance = int(redis.get(BALANCE).decode())
    if redis.set(BALANCE, balance + count) == 1:
        return count, True
    return count, False


@acquire_lock(redis, BALANCE_REDIS_LOCK, TIMEOUT, MAX_ACQUIRE_TIME)
def deduct_balance(count):
    """
    Deducts balance.

    :param      count:  要减去的金额
    """
    balance = int(redis.get(BALANCE).decode())
    if redis.set(BALANCE, balance + count) == 1:
        return count, True
    return count, False


def test():
    """
    test
    """

    from concurrent.futures import ThreadPoolExecutor

    CHANGE_TIMES = 10
    success = 0
    failed = []

    def done_callback(r):
        nonlocal success
        ret, ok = r.result()
        if ok:
            if ret[1]:
                success += 1
            else:
                failed.append(ret[0])
        else:
            failed.append(ret[0][0])

    # balance_changes = [random.randint(0, 10) for i in range(CHANGE_TIMES)]
    balance_changes = [1, -1, 1, -1, 1]  # sum: 1

    executor = ThreadPoolExecutor(max_workers=8)
    for balance_change in balance_changes:
        if balance_change >= 0:
            m = increase_balance
        else:
            m = deduct_balance
        f = executor.submit(m, balance_change)
        f.add_done_callback(done_callback)
    executor.shutdown()

    # Fetch result
    balance = int(redis.get("balance").decode())
    print(balance_changes)
    print(failed)
    print(f"Success: {success}")
    print(f"Balance=Changes: {balance == sum(balance_changes)-sum(failed)}")
    print(f"Balance: {balance}")


if __name__ == "__main__":
    for i in range(10):
        # 初始化账户
        redis.set(BALANCE, 0)
        test()

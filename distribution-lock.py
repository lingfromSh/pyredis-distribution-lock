import redis

redis = redis.Redis(host='localhost', port=6379, db=0)

# Lock On
LOCK_ON = True

# 账户
BALANCE = "balance"

# 初始化账户
redis.set(BALANCE, 0)

# 分布式锁
BALANCE_REDIS_LOCK = "balance-lock"

# 最大重试
MAX_RETRY = 15


def acquire_lock(skip=False) -> bool:
    """
    Acquire a lock.

    :param      skip:  The skip
    :type       skip:  bool

    :returns:   { 成功True,失败False }
    :rtype:     bool
    """

    if skip:
        return True

    retry_count = 0
    while retry_count < MAX_RETRY:
        code = redis.setnx(BALANCE_REDIS_LOCK, 1)
        if code == 1:
            return True
    return False


def release_lock() -> bool:
    """
    Releases a lock.

    :returns:   { 成功True, 失败False }
    :rtype:     bool
    """
    code = redis.delete(BALANCE_REDIS_LOCK)
    return code == 1


def increase_balance(count) -> int:
    """
    Increases balance.

    :param      count:  要添加的金额

    :returns:   { 失败-1,成功1 }
    :rtype:     int
    """
    if acquire_lock(not LOCK_ON):
        balance = int(redis.get(BALANCE).decode())
        redis.set(BALANCE, balance + count)
        release_lock()
        return 1
    else:
        return -1


def deduct_balance(count) -> int:
    """
    Deducts balance.

    :param      count:  要减去的金额

    :returns:   { 失败-1,成功1 }
    :rtype:     int
    """
    if acquire_lock(not LOCK_ON):
        balance = int(redis.get(BALANCE).decode())
        redis.set(BALANCE, balance + count)
        release_lock()
        return 1
    else:
        return -1


def test():
    """
    test
    """

    import random
    from concurrent.futures import ThreadPoolExecutor

    CHANGE_TIMES = 10
    success = 0

    def done_callback(r):
        nonlocal success
        if r.result():
            success += 1

    balance_changes = [random.randint(-1000, 1000) for i in range(CHANGE_TIMES)]

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
    print(f"Success: {success}")
    print(f"Balance=Changes: {balance == sum(balance_changes)}")
    print(f"Balance: {balance}")


if __name__ == "__main__":
    print("Test with lock")
    LOCK_ON = True
    test()

    print("Test without lock")
    LOCK_ON = False
    test()

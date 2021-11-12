# PyRedis Distribution Lock

## Introduction

It's just a simple implementation of distribution lock.

We could use redis distribution lock to manipulate some shared resources safely in distributed context.

## Tests

You could quickly test

```shell
python3 -m tests.xxx
```

## Quick Start

You could take adventage of a redis distribution lock in a very simple way.

```python3
import redis
import lock

r = redis.Redis(host='localhost', port=6379, db=0)

# if-else
def deduct_inventory(...):
    lock = lock.RedisDistributionLock()
    if lock.acquire(...):
        ...
	lock.release()

# with
def deduct_inventory(...):
    with lock.RedisDistributionLock():
        ...
```

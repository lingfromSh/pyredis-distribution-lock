# PyRedis Distribution Lock

## Introduction

It's just a simple implementation of distribution lock.

We could use redis distribution lock to manipulate some shared resources safely in distributed context.

## Quick Start

You could take adventage of a redis distribution lock in a very simple way.

```python3
import redis
import lock

r = redis.Redis(host='localhost', port=6379, db=0)

@lock.acquire_lock(r, "lock", 10, 10)
def deduct_inventory(...):
	...
```
import time


class RedisDistributionLock:
    """
    This class describes a redis distribution lock.
    """

    ACQUIRED = 1
    SUCCESS = 1
    FAILURE = -1
    MAX_WAIT = 60

    def __init__(self, name, rclient):
        assert name, "missing name"
        assert rclient, "missing redis client"

        self.name = name
        self.rclient = rclient

    def acquire(self, wait=None, acquire_time=30) -> bool:
        """
        Acquires the lock

        :param      wait:          The wait
        :type       wait:          { type_description }
        :param      acquire_time:  The acquire time
        :type       acquire_time:  int

        :returns:   { description_of_the_return_value }
        :rtype:     bool
        """

        if wait is None:
            wait = RedisDistributionLock.MAX_WAIT

        end = time.time() + wait
        while time.time() < end:
            if (
                self.rclient.setnx(self.name, RedisDistributionLock.ACQUIRED)
                == RedisDistributionLock.SUCCESS
            ):
                self.rclient.expire(self.name, acquire_time)
                return True

            if self.rclient.ttl(self.name) == RedisDistributionLock.FAILURE:
                self.rclient.expire(self.name, min(acquire_time, wait))

        return False

    def release(self) -> bool:
        """
        Releases the lock

        :returns:   { description_of_the_return_value }
        :rtype:     bool
        """
        return self.rclient.delete(self.name) == RedisDistributionLock.SUCCESS

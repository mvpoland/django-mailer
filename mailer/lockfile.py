from lockfile import LockBase, FileLock, LinkFileLock, AlreadyLocked, LockTimeout


__all__ = [
    "LockBase",
    "FileLock",
    "LinkFileLock",
    "NoopLock",
    "AlreadyLocked",
    "LockTimeout",
]


class NoopLock(LockBase):
    def acquire(self, timeout=None):
        pass

    def release(self):
        pass

    def is_locked(self):
        return False

    def i_am_locking(self):
        return True

    def break_lock(self):
        pass

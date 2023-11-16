from pathlib import Path

from filelock import FileLock


def make_lock(func):
    def lock_func():
        lock = FileLock(Path(__file__).parent / "keepass.lock")
        lock.acquire(timeout=-1)
        try:
            func()
        finally:
            lock.release()

    return lock_func

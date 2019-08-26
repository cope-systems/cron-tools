import fcntl
import os
import signal
import errno


class FlockTimeout(Exception):
    pass


class FlockLock(object):
    def __init__(self, fd, timeout=None, flock_mode=fcntl.LOCK_EX):
        self.fd = fd
        self.timeout = timeout
        self.flock_mode = flock_mode

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __del__(self):
        self.close()

    @classmethod
    def from_file(cls, filename, timeout=None):
        return cls(os.open(filename, os.O_RDWR | os.O_CREAT), timeout=timeout)

    def acquire(self):
        if self.timeout is None:
            fcntl.flock(self.fd, self.flock_mode)
        else:
            original_handler = signal.signal(signal.SIGALRM, lambda *args, **kwargs: None)
            try:
                signal.alarm(self.timeout)
                fcntl.flock(self.fd, self.flock_mode)
            except IOError as e:
                if e.errno != errno.EINTR:
                    raise e
                else:
                    raise FlockTimeout("Timed out attempting to acquire flock.")
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)

    def release(self):
        fcntl.flock(self.fd, fcntl.LOCK_UN)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

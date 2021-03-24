import random
import logging
import os
import time
from functools import wraps


def logger_create():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s :: %(message)s")
    file_handler = logging.FileHandler(filename=os.path.normpath("./log/logger.log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def ordinal_represent(number: int):
    suf = lambda num: "%d%s" % (
        num,
        {1: "st", 2: "nd", 3: "rd"}.get(num if num < 20 else num % 10, "th"),
    )
    return suf(number)


def retry(
    exception: tuple,
    tries: int,
    delay: int,
    backoff: int,
    logger: logging.Logger = None,
) -> callable:
    def retrier(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args: tuple, **kwargs: dict):
            err = None
            local_tries, local_delay = tries, delay
            loggers = logger_create()

            while local_tries:
                try:
                    return func(*args, **kwargs)
                except exception as exc:
                    local_tries -= 1
                    err = exc
                    time_now = time.localtime()
                    if logger:
                        loggers.info(
                            f"Retrying {func.__name__} {ordinal_represent(tries-local_tries)} time! "
                        )
                    else:
                        print(
                            f"{time.asctime(time_now)} :: Retrying {func.__name__} "
                            f"{ordinal_represent(tries-local_tries)} time!"
                        )
                    time.sleep(local_delay)
                    local_delay += backoff
            return err

        return wrapper

    return retrier


@retry(Exception, tries=3, delay=2, backoff=0, logger=logging.getLogger("my logger"))
def random_numbers_interval(p, q):
    random_number = random.uniform(0, 1)
    if random_number < p:
        raise Exception("less than lower bound")
    if random_number > q:
        raise Exception("greater than upper bound")
    return random_number


if __name__ == "__main__":
    print(random_numbers_interval(0.88888888, 1))

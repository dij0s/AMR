import time
from collections import defaultdict
from typing import Callable


class Benchmark:
    """
    This class is used to benchmark the performance of the simulation.
    It is implemented as a singleton to ensure that only one instance is created.
    """

    # singleton instance
    _instance: "Benchmark" = None

    def __init__(self):
        """
        Benchmark constructor.

            Parameters:
                None

            Returns:
                None
        """

        # create dictionaries to store
        # the elapsed time and space for
        # each function
        self._func_times: defaultdict[str, float] = defaultdict(float)
        self._func_space: defaultdict[str, float] = defaultdict(float)

    def __new__(cls):
        # check for existing instance
        # and create new instance if
        # necessary
        if cls._instance is None:
            cls._instance: "Benchmark" = super(Benchmark, cls).__new__(cls)
            cls._instance.start: float = time.time()

        return cls._instance

    def time(self, f: Callable):
        """
        Decorator to measure the time of a function.
        The time is saved in the _func_times dictionary.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper function to measure the time of a function.
            """

            # start time [s]
            start: float = time.time()

            # call function
            result = f(*args, **kwargs)

            # elapsed time [s]
            elapsed: float = time.time() - start

            # save elapsed time
            self._func_times[f.__name__] += elapsed

            # return result
            return result

        return wrapper

    @property
    def elapsed(self) -> float:
        """
        Get the elapsed time [s] since the start of the benchmark.
        """

        return time.time() - self.start

    @property
    def func_times(self) -> defaultdict:
        """
        Get the elapsed time [s] for each function.
        """

        return self._func_times

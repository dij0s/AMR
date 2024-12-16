import os
import time
from collections import defaultdict
from functools import wraps
from typing import Callable

import psutil


class Benchmark:
    """
    This class is used to benchmark the performance of the simulation.
    It is implemented as a singleton to ensure that only one instance is created.
    """

    # singleton instance
    _instance: "Benchmark" = None
    # flag to check if the
    # class is initialized
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Benchmark, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Constructor of the Benchmark class.

            Parameters:
                None

            Returns:
                None
        """

        # check if the class
        # is initialized
        if not Benchmark._initialized:
            # dictionaries to store
            # the elapsed time and space
            # for each function
            self._func_times: defaultdict[str, float] = defaultdict(float)
            self._func_space: defaultdict[str, float] = defaultdict(float)

            # get current program process
            self._process: int = psutil.Process(os.getpid())

            self.start: float = time.time()
            Benchmark._initialized = True

    def repeat(self, f: Callable):
        """
        Decorator to execute a function n times.
        It shall only be used to exectue a function with no return value.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper function to execute a function n times.
            """

            # number of executions
            n: int = kwargs.pop("n", 1)

            # execute function n times
            for i in range(n):
                # execute function
                f(*args, **kwargs)

                # sleep for 10 seconds
                # as a way to cool down
                if n > 1 and i < n - 1:
                    time.sleep(10)

        return wrapper

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

    def space(self, f: Callable):
        """
        Decorator to measure the space of a function.
        The space is saved in the _func_space dictionary.
        """

        @wraps(f)
        def wrapper(*args, **kwargs):
            """
            Wrapper function to measure the space of a function.
            """

            # memory usage before
            # function call
            mem_before: float = self._process.memory_info().rss

            # call function
            result = f(*args, **kwargs)

            # memory usage after
            # function call
            mem_after: float = self._process.memory_info().rss

            # memory used [MB]
            mem_used: float = (mem_after - mem_before) / 1024.0 / 1024.0

            # save memory used
            self._func_space[f.__name__] += mem_used

            # return result
            return result

        return wrapper

    def reset(self) -> None:
        """
        Reset the benchmark.

            Parameters:
                None

            Returns:
                None
        """

        self._func_times.clear()
        self.start = time.time()

    def display(self) -> None:
        """
        Display the benchmark results.

            Parameters:
                None

            Returns:
                None
        """

        print("\nBenchmarked time:")
        for key, value in self._func_times.items():
            print(f"Function '{key}':\t{value:.4}s")

        print("\nBenchmarked memory usage:")
        for key, value in self._func_space.items():
            print(f"Function '{key}':\t{value:.4}MB")

    @property
    def elapsed(self) -> float:
        """
        Get the elapsed time since the start of the benchmark.

            Parameters:
                None

            Returns:
                float: Elapsed time [s]
        """

        return time.time() - self.start

    @property
    def func_times(self) -> defaultdict:
        """
        Get the elapsed time for each function.

            Parameters:
                None

            Returns:
                defaultdict: Elapsed time for each function [s]
        """

        return self._func_times

    @property
    def func_space(self) -> defaultdict:
        """
        Get the memory used for each function.

            Parameters:
                None

            Returns:
                defaultdict: Memory used for each function [MB]
        """

        return self._func_space

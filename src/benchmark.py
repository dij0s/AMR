import os
import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Optional

import psutil


class Benchmark:
    """
    This class is used to benchmark the performance of the simulation.
    It is implemented as a singleton to ensure that only one instance is created.
    """

    # singleton instance
    _instance: Optional["Benchmark"] = None
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
            # for each function with the
            # number of calls
            self._func_times: defaultdict[str, tuple[float, int]] = defaultdict(
                lambda: (0.0, 0)
            )
            self._func_space: defaultdict[str, tuple[float, int]] = defaultdict(
                lambda: (0.0, 0)
            )

            # get current program process
            self._process: psutil.Process = psutil.Process(os.getpid())

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
        Decorator to measure the time of a function and
        the number of times it is called.
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
            current_time, calls = self._func_times[f.__name__]
            self._func_times[f.__name__] = (current_time + elapsed, calls + 1)

            # return result
            return result

        return wrapper

    def space(self, f: Callable):
        """
        Decorator to measure the space of a function and
        the number of times it is called.
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
            current_memory, calls = self._func_space[f.__name__]
            self._func_space[f.__name__] = (current_memory + mem_used, calls + 1)

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
        self._func_space.clear()
        self.start = time.time()

    def display(self) -> None:
        """
        Display the benchmark results.

            Parameters:
                None

            Returns:
                None
        """

        print("BENCHMARKED TIME\nFunction name Total time [s] (Number of calls)")
        for key, value in self._func_times.items():
            print(f"{key}\t\t{value[0]:.4} ({value[1]})")

        print("BENCHMARKED SPACE\nFunction name\tMemory used [MB] (Number of calls)")
        for key, value in self._func_space.items():
            print(f"{key}\t\t{value[0]:.4} ({value[1]})")

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

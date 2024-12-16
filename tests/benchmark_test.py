from src.benchmark import Benchmark


def test_benchmark():
    """
    Test the benchmark class.
    """

    # create a benchmark instance
    benchmark = Benchmark()

    # creating a second instance
    # should return the same instance
    benchmark2 = Benchmark()
    assert benchmark is benchmark2

    # test time decorator
    # test basic argument-less
    # function
    @benchmark.time
    def test_func():
        return 1

    res = test_func()
    assert res == 1

    # test time decorator
    # test function with arguments
    @benchmark.time
    def test_func_args(a: int, b: int):
        return a + b

    res = test_func_args(1, 2)
    assert res == 3

    # test elapsed time
    assert benchmark.elapsed > 0

    # test func_times
    assert benchmark.func_times["test_func"] > 0
    assert benchmark.func_times["test_func_args"] > 0

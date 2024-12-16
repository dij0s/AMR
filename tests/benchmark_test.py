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

    # test space decorator
    # test basic argument-less
    # function
    @benchmark.space
    def test_func():
        return 1

    res = test_func()
    assert res == 1

    # test space decorator
    # test function with arguments
    # and return value
    @benchmark.space
    def test_func_args(a: int, b: int):
        return a + b

    res = test_func_args(1, 2)
    assert res == 3

    # test space decorator
    # test function with many
    # array operations
    @benchmark.space
    def test_func_array(n: int):
        return [i for i in range(n)]

    res = test_func_array(10000)

    # cannot test the size the array
    # took in memory as it is system
    # dependent
    assert benchmark.func_space is not None

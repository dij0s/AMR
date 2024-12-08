from src.some_module import SomeModule


def test_some_method():
    x: int = 16.0
    assert SomeModule.some_method(x) == 4.0

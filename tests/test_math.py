from math_operations import add, evaluate_polynomial, multiply, subtract


def test_add():
    assert add(5, 3) == 8
    assert add(-2, 7) == 5


def test_subtract():
    assert subtract(10, 4) == 6
    assert subtract(5, 8) == -3


def test_multiply():
    assert multiply(6, 7) == 42
    assert multiply(0, 99) == 0


def test_evaluate_polynomial():
    assert evaluate_polynomial([3, 2, 1], 4) == 57
    assert evaluate_polynomial([1, 0, 0], 5) == 25
    assert evaluate_polynomial([5], 10) == 5

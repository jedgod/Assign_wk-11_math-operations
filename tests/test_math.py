from math_operations import add, evaluate_polynomial, multiply, polynomial_steps, subtract


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


def test_polynomial_steps_matches_horner_sequence():
    steps = polynomial_steps([3, 2, 1], 4)

    assert steps == [
        "Step 1: (0 * 4) + 3 = 3",
        "Step 2: (3 * 4) + 2 = 14",
        "Step 3: (14 * 4) + 1 = 57",
    ]


def test_polynomial_steps_single_coefficient():
    steps = polynomial_steps([5], 10)

    assert steps == ["Step 1: (0 * 10) + 5 = 5"]

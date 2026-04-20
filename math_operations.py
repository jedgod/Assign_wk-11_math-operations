def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def evaluate_polynomial(coefficients: list, x: float) -> float:
    """Evaluate polynomial coefficients ordered highest degree to constant."""
    result = 0
    for coeff in coefficients:
        result = result * x + coeff
    return result


__all__ = ["add", "subtract", "multiply", "evaluate_polynomial"]

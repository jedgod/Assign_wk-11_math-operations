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


def polynomial_steps(coefficients: list, x: float) -> list:
    """Return Horner step strings for polynomial evaluation."""
    steps = []
    result = 0
    for index, coeff in enumerate(coefficients, start=1):
        previous = result
        result = result * x + coeff
        steps.append(
            f"Step {index}: ({previous} * {x}) + {coeff} = {result}"
        )
    return steps


__all__ = [
    "add",
    "subtract",
    "multiply",
    "evaluate_polynomial",
    "polynomial_steps",
]

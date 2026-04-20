import sys

import yaml

from math_operations import (
    add,
    evaluate_polynomial,
    multiply,
    polynomial_steps,
    subtract,
)


def load_config():
    try:
        with open("config.yml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Config error: {e}")
        sys.exit(1)


def main():
    config = load_config()
    nums = config.get("numbers", {})
    poly = config.get("polynomial", {})

    print("Math Operations App Started")
    print("=" * 40)
    print(
        f"Addition:       {nums.get('a')} + {nums.get('b')} = "
        f"{add(nums.get('a', 0), nums.get('b', 0))}"
    )
    print(
        f"Subtraction:    {nums.get('a')} - {nums.get('b')} = "
        f"{subtract(nums.get('a', 0), nums.get('b', 0))}"
    )
    print(
        f"Multiplication: {nums.get('a')} x {nums.get('b')} = "
        f"{multiply(nums.get('a', 0), nums.get('b', 0))}"
    )

    coeffs = poly.get("coefficients", [0])
    x = poly.get("x_value", 0)
    print("Polynomial computation steps:")
    for step in polynomial_steps(coeffs, x):
        print(f"  {step}")
    print(f"Polynomial:     {coeffs} at x={x} = {evaluate_polynomial(coeffs, x)}")
    print("=" * 40)
    print("All operations completed successfully!")


if __name__ == "__main__":
    main()

# Assign_wk-11_math-operations

## A. Introduction
This project is a Python-based math operations application developed for Week 11 coursework in Software Engineering II. The app reads input values from config.yml and performs addition, subtraction, multiplication, and polynomial evaluation. The polynomial logic uses Horner's method and now prints each computation step so users can follow the full solution process, not just the final answer.

## B. Objectives/Goals
1. Build a working command-line math application with clean modular functions.
2. Support four core operations: add, subtract, multiply, and polynomial evaluation.
3. Provide clear runtime output that includes polynomial step-by-step computation.
4. Add automated tests using pytest for both operation logic and main workflow sanity checks.
5. Set up a 3-stage CI/CD pipeline for test, production validation, and run.
6. Publish and maintain the project on both GitLab and GitHub.

## C. Implementation Steps
1. Created core math logic in math_operations.py:
	add(a, b), subtract(a, b), multiply(a, b), evaluate_polynomial(coefficients, x), and polynomial_steps(coefficients, x).
2. Built main.py to:
	load YAML configuration from config.yml,
	execute all operations,
	display polynomial computation steps,
	and print the final polynomial result.
3. Wrote unit tests:
	tests/test_math.py for operation correctness and polynomial step verification,
	tests/test_main.py for config loading, invalid config behavior, and output sanity.
4. Configured CI/CD in .gitlab-ci.yml with three stages:
	test, production, and run.
5. Established version-control workflow with commits and dual remote push to GitLab and GitHub.

## D. Problems Encountered
1. Repository scope issue:
	The project was initially under a higher-level Git repository, which risked adding unrelated personal files. This was fixed by initializing a dedicated repository in the project folder.
2. Missing dependencies:
	pytest and pyyaml were not initially available in the runtime used for execution. These were installed in the project environment.
3. Duplicate code blocks:
	Some files contained duplicate sections, causing old logic to override updated behavior. Duplicates were removed to keep one canonical implementation.
4. Polynomial interpretation mismatch:
	Coefficient order and expected values were inconsistent during testing. Logic and tests were aligned to highest-degree-to-constant order.
5. Output visibility confusion:
	Polynomial steps appeared missing in some runs due to context/version confusion. Current main execution now consistently prints every step.

## E. Conclusion
The Week 11 math operations app is fully implemented, tested, and integrated with CI/CD. It now provides both final answers and transparent polynomial step-by-step computation, improving correctness and explainability. With automated tests passing and synchronized GitLab/GitHub repositories, the project meets its core functional, quality, and delivery goals.

## Advanced Math UI

Run the interactive mathematics application:

```bash
pip install streamlit sympy numpy matplotlib scipy
streamlit run app.py
```

Features:

Algebra simplification
Equation solving
Derivatives
Integrals
Function graphing
Matrix operations
Complex number calculation
System of equations solving

Your folder should become:

```text
ASSIGN_ENHANCEMENT/
|
|- app.py
|- main.py
|- math_operations.py
|- config.yml
|- tests/
|- README.md
\- .gitlab-ci.yml
```

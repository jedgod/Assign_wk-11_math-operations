# Assign_wk-11_math-operations

## Project Overview
This project is a Python software development and DevOps environment built for Software Engineering II. It demonstrates how an application is stored in remote repositories, configured with dependencies, tested automatically, validated in a pipeline, executed locally, and prepared for production deployment.

The application has two entry points:

1. A command-line math operations program in `main.py`
2. An interactive Streamlit-based math interface in `app.py`

The command-line program reads values from `config.yml` and performs addition, subtraction, multiplication, and polynomial evaluation. The polynomial logic uses Horner's method and prints each computation step. The Streamlit application extends the project into a richer user-facing interface for symbolic and numerical mathematics.

## Assignment Alignment
This repository satisfies the assignment goal of showing a software development pipeline with the following elements:

1. Remote version control in GitLab and GitHub
2. Dependency management with `requirements.txt`
3. Source code organization across multiple Python modules
4. Automated testing with `pytest`
5. Validation and execution through GitLab CI/CD
6. Production-ready deployment logic for AWS S3 and Elastic Beanstalk

## Tools and Libraries
The project uses these main tools, frameworks, and libraries:

- Python 3.11
- Git
- GitLab CI/CD
- GitHub
- PyYAML
- pytest
- Streamlit
- SymPy
- NumPy
- Matplotlib
- SciPy
- AWS CLI and Elastic Beanstalk CLI in deployment jobs

## Repository Storage
The code is stored remotely in both platforms required for collaborative DevOps workflow:

- GitLab: primary CI/CD pipeline host
- GitHub: secondary mirrored repository

## Project Structure
```text
ASSIGN_ENHANCEMENT/
|
|- app.py
|- main.py
|- math_operations.py
|- config.yml
|- requirements.txt
|- Procfile
|- tests/
|  |- test_main.py
|  \- test_math.py
|- README.md
\- .gitlab-ci.yml
```

## Application Components
### 1. Core Math Module
`math_operations.py` contains the reusable functions:

- `add(a, b)`
- `subtract(a, b)`
- `multiply(a, b)`
- `evaluate_polynomial(coefficients, x)`
- `polynomial_steps(coefficients, x)`

### 2. Command-Line Program
`main.py`:

- loads values from `config.yml`
- runs the math operations
- prints step-by-step polynomial evaluation
- serves as the production execution check in CI

### 3. Interactive UI
`app.py` provides an advanced math interface using Streamlit. It supports:

- step-by-step solving
- algebra simplification
- equation solving
- derivatives
- integrals
- function graphing
- matrix operations
- complex numbers
- systems of equations

## Testing Strategy
Automated tests are stored in `tests/`.

- `tests/test_math.py` validates core math functions and Horner-step output
- `tests/test_main.py` validates config loading, error handling, and default output behavior

Run tests locally with:

```bash
python -m pytest tests/ -v
```

## GitLab CI/CD Pipeline
The GitLab pipeline is defined in `.gitlab-ci.yml` and demonstrates a multi-stage DevOps workflow.

### Stage 1: `test`
- installs dependencies
- runs `pytest`
- exports `test-results.xml` as a CI artifact

### Stage 2: `validate`
- compiles Python files with `python -m py_compile`
- validates `config.yml`
- verifies that the Streamlit application imports correctly

### Stage 3: `production`
- executes `python main.py`
- confirms the math application runs successfully on the main branch

### Stage 4: `deploy`
- uploads test artifacts to AWS S3 when AWS variables are configured
- deploys the application bundle to AWS Elastic Beanstalk when deployment variables are configured

The deploy jobs are intentionally conditional. If AWS secrets and deployment variables are not set in GitLab CI/CD settings, the deploy jobs are skipped instead of failing the pipeline.

## How the Project Is Built, Tested, and Run
### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the command-line application
```bash
python main.py
```

### Run the Streamlit application
```bash
streamlit run app.py
```

### Validate syntax manually
```bash
python -m py_compile main.py math_operations.py app.py
```

## Production Readiness
This project demonstrates two production-oriented paths:

1. Local production-style execution through `python main.py`
2. Cloud deployment readiness through S3 artifact upload and Elastic Beanstalk deployment jobs

The repository also includes a `Procfile` for platform-style startup of the Streamlit app:

```text
web: streamlit run app.py --server.port 8080 --server.address 0.0.0.0 --server.headless true
```

## Problems Solved During Development
Key issues addressed during the project included:

1. dependency installation gaps
2. duplicate configuration content
3. polynomial coefficient interpretation mismatches
4. CI import-path failures in GitLab runners
5. deploy-job failures when AWS variables were not configured

These fixes improved both the application behavior and the stability of the pipeline.

## Conclusion
This project is not only a math application; it is a complete software development workflow example. It shows how code is written, stored remotely, tested automatically, validated in CI, executed as an application, and prepared for production deployment. That makes it aligned with the assignment's DevOps and pipeline objectives.

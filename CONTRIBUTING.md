# 🤝 Contributing to COVID-19 Vaccination Analysis

Thank you for your interest in contributing! Contributions, bug reports, and feature suggestions are all welcome.

## 🐛 Reporting Bugs

If you find a bug, please [open an issue](https://github.com/sehaan-1/covid-vaccination-analysis/issues) and include:

*   A clear description of the bug
*   Steps to reproduce it
*   Expected vs. actual behaviour
*   Your Python and Streamlit versions (`python --version`, `streamlit --version`)

## 💡 Suggesting Features

Have an idea? Open an issue with the label `enhancement` and describe:

*   The problem you're trying to solve
*   How the feature would work
*   Any relevant examples or references

## 🛠️ Setting Up for Development

1.  Fork the repository and clone your fork:
    ```bash
    git clone https://github.com/YOUR_USERNAME/covid-vaccination-analysis.git
    cd covid-vaccination-analysis
    ```

2.  Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    pip install pytest       # for running tests
    ```

3.  Create a new branch for your change:
    ```bash
    git checkout -b feature/your-feature-name
    ```

## ✅ Running Tests

The test suite uses `pytest`. Make sure it passes before submitting a pull request:

```bash
pytest tests/ -v
```

## 📦 Submitting a Pull Request

1.  Commit your changes with a clear, descriptive message:
    ```bash
    git commit -m "feat: add heatmap visualization for regional coverage"
    ```

2.  Push to your fork and open a Pull Request against the `main` branch.

3.  Describe what you changed and why in the PR description.

## 📋 Code Style

*   Follow [PEP 8](https://peps.python.org/pep-0008/) for Python formatting.
*   Keep functions small and focused.
*   Add docstrings to any new public functions.
*   Use descriptive variable names.

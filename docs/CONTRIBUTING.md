# Contributing to CV Paper Piano

Thank you for your interest in contributing!

## 1. Setting Up the Development Environment

### Prerequisites
* FluidSynth
* Python 3.12+
* Git
* SoundFont
* Virtual Environment
* Environment File

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ManiZoljanahi/cv-paper-piano.git
    cd cv-paper-piano
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate # On Linux / Mac: source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a environment file:**
    ```bash
    copy .env.example .env # On Linux / Mac: cp .env.example .env
    ```

## 2. Project Structure
* `src/`: Core application source code.
* `tests/`: Pytest unit and integration tests.
* `assets/`: Images, SoundFonts, and Database files.
* `examples/`: Diagnostic scripts (e.g., `check_camera.py`).
* `.github/` & `.gitlab/`: Platform-specific issue and merge/pull request templates.

## 3. Running Tests
We use `pytest` for ensuring logic integrity. Before submitting any changes, ensure all tests pass.

**Run all tests:**
```bash
pytest -v
```

**Run specific test modules:**
```bash
pytest -v tests/test_vision.py
```

## 4. Coding Standards
- Style: Follow PEP 8 guidelines.
- Docstrings: All classes and functions must have docstrings explaining their purpose, arguments, and return values.
- Type Hinting: Use Python type hints where possible (e.g., def calculate(x: float) -> int:)

## 5. Pull Request / Merge Request Process
1. Create a new branch: `git checkout -b feature/AmazingFeature`.
2. Commit your changes.
3. Push to the branch.
4. Open a Pull Request (GitHub) or Merge Request (GitLab). Please utilize the provided templates to describe the "Why" and "How" of your changes.
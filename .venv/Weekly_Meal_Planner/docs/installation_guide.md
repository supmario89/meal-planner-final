# Installation Guide

## Prerequisites
- Python 3.12 or later
- Pip

## Steps
1. Clone the repository.
    ```bash
    git clone https://github.com/supmario89/weekly_meal_planner.git
    cd weekly_meal_planner
    ```
2. Create a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install dependencies.
    ```bash
    pip install -r requirements.txt
    ```
4. Set the `PYTHONPATH`.
    ```bash
    export PYTHONPATH="${PYTHONPATH}:src"
    ```
5. Run the project.
    ```bash
    python src/send_email.py
    ```
"""
Development Scripts

Custom tasks for development workflow.
"""

import os
import subprocess
import sys


def show_help():
    """Show available Poetry scripts."""
    print("🚀 Time Server - Available Commands")
    print("=" * 40)
    print("Development:")
    print("  poetry run dev-server    # Start Django server")
    print("  poetry run test          # Run tests")
    print("  poetry run test-cov      # Tests with coverage")
    print("  poetry run lint          # Run linting")
    print("  poetry run format        # Format code (black, isort, flake8)")
    print("  poetry run clean         # Clean artifacts")
    print()
    print("Docker:")
    print("  poetry run docker-build  # Build image")
    print("  poetry run docker-run    # Run container")
    print("  poetry run docker-stop   # Stop container")
    print("  poetry run docker-logs   # Show logs")
    print()
    print("Database:")
    print("  poetry run db-migrate    # Run migrations")
    print("  poetry run db-reset      # Reset database")
    print("  poetry run db-seed       # Seed database")
    print()
    print("Deployment:")
    print("  poetry run deploy-staging # Deploy to staging")
    print("  poetry run deploy-prod    # Deploy to production")
    print()
    print("💡 Tip: Use 'poetry run <command>' to execute any script")


def start_dev_server():
    """Start the Django development server."""
    print("🚀 Starting Django development server...")
    try:
        subprocess.run(
            [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    try:
        subprocess.run(["poetry", "run", "pytest", "tests/"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        sys.exit(1)


def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    print("🧪 Running tests with coverage...")
    try:
        subprocess.run(
            [
                "poetry",
                "run",
                "pytest",
                "--cov=apps",
                "--cov=api.urls",
                "--cov-report=html:reports/htmlcov",
                "--cov-report=term-missing",
                "--cov-report=xml:reports/coverage.xml",
            ],
            check=True,
        )
        print("📊 Coverage report generated in reports/htmlcov/index.html")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        sys.exit(1)


def run_linting():
    """Run code linting."""
    print("🔍 Running code linting...")
    try:
        # Run flake8
        subprocess.run(["poetry", "run", "flake8", "."], check=True)
        print("✅ Flake8 passed")

        # Run isort check
        subprocess.run(["poetry", "run", "isort", "--check-only", "."], check=True)
        print("✅ Import sorting is correct")

    except subprocess.CalledProcessError as e:
        print(f"❌ Linting failed: {e}")
        sys.exit(1)


def run_formatting():
    """Run code formatting (black, isort, flake8) against non-test code."""
    print("🎨 Formatting code...")
    try:
        # Define paths to format (exclude tests)
        paths_to_format = ["apps/", "api/", "scripts/", "manage.py", "time_server/"]

        # Run black on non-test code
        print("Running black...")
        subprocess.run(["poetry", "run", "black"] + paths_to_format, check=True)
        print("✅ Black formatting complete")

        # Run isort on non-test code
        print("Running isort...")
        subprocess.run(["poetry", "run", "isort"] + paths_to_format, check=True)
        print("✅ Import sorting complete")

        # Run flake8 on non-test code
        print("Running flake8...")
        subprocess.run(["poetry", "run", "flake8"] + paths_to_format, check=True)
        print("✅ Flake8 linting complete")

        print("🎉 All formatting tools completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Formatting failed: {e}")
        sys.exit(1)


def clean_project():
    """Clean project artifacts."""
    print("🧹 Cleaning project...")

    # Remove Python cache
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                print(f"Removing {cache_path}")
                subprocess.run(["rm", "-rf", cache_path])
                dirs.remove(dir_name)

    # Remove .pyc files
    subprocess.run(["find", ".", "-name", "*.pyc", "-delete"])

    # Remove reports directory
    if os.path.exists("reports"):
        print("Removing reports directory")
        subprocess.run(["rm", "-rf", "reports"])

    # Remove .coverage file
    if os.path.exists(".coverage"):
        print("Removing .coverage file")
        os.remove(".coverage")

    print("✅ Project cleaned")

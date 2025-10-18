"""
Deployment Scripts

Custom tasks for deployment operations.
"""

import subprocess
import sys


def deploy_staging():
    """Deploy to staging environment."""
    print("🚀 Deploying to staging...")
    try:
        # Run tests first
        print("🧪 Running tests...")
        subprocess.run(["poetry", "run", "pytest", "--cov=apps"], check=True)

        # Build Docker image
        print("🐳 Building Docker image...")
        subprocess.run(
            ["docker", "build", "-t", "time-server:staging", "-f", "Dockerfile", "."],
            check=True,
        )

        # Deploy to staging (example with docker-compose)
        print("🚀 Deploying to staging environment...")
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.staging.yml", "up", "-d"],
            check=True,
        )

        print("✅ Staging deployment completed")
        print("🌐 Staging URL: https://staging.time-server.example.com")

    except subprocess.CalledProcessError as e:
        print(f"❌ Staging deployment failed: {e}")
        sys.exit(1)


def deploy_production():
    """Deploy to production environment."""
    print("🚀 Deploying to production...")

    # Confirm production deployment
    print("⚠️ WARNING: This will deploy to PRODUCTION!")
    response = input("Are you sure you want to deploy to production? (yes/no): ")

    if response.lower() != "yes":
        print("❌ Production deployment cancelled")
        return

    try:
        # Run full test suite
        print("🧪 Running full test suite...")
        subprocess.run(
            [
                "poetry",
                "run",
                "pytest",
                "--cov=apps",
                "--cov-report=html:reports/htmlcov",
            ],
            check=True,
        )

        # Run linting
        print("🔍 Running linting...")
        subprocess.run(["poetry", "run", "flake8", "."], check=True)

        # Build production Docker image
        print("🐳 Building production Docker image...")
        subprocess.run(
            [
                "docker",
                "build",
                "-t",
                "time-server:production",
                "-f",
                "Dockerfile.prod",
                ".",
            ],
            check=True,
        )

        # Deploy to production
        print("🚀 Deploying to production environment...")
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.prod.yml", "up", "-d"], check=True
        )

        print("✅ Production deployment completed")
        print("🌐 Production URL: https://time-server.example.com")

    except subprocess.CalledProcessError as e:
        print(f"❌ Production deployment failed: {e}")
        sys.exit(1)


def rollback():
    """Rollback to previous deployment."""
    print("🔄 Rolling back deployment...")
    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.prod.yml", "rollback"], check=True
        )
        print("✅ Rollback completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Rollback failed: {e}")
        sys.exit(1)


def health_check():
    """Check application health."""
    print("🏥 Checking application health...")
    try:
        # Check if application is responding
        subprocess.run(
            ["curl", "-f", "http://localhost:8000/api/health-check/"], check=True
        )
        print("✅ Application is healthy")
    except subprocess.CalledProcessError as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)

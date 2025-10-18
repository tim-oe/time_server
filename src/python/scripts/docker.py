"""
Docker Scripts

Custom tasks for Docker operations.
"""

import subprocess
import sys


def build_image():
    """Build Docker image for the application."""
    print("🐳 Building Docker image...")
    try:
        subprocess.run(
            ["docker", "build", "-t", "time-server:latest", "-f", "Dockerfile", "."],
            check=True,
        )
        print("✅ Docker image built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e}")
        sys.exit(1)


def run_container():
    """Run Docker container."""
    print("🐳 Starting Docker container...")
    try:
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                "time-server-container",
                "-p",
                "8000:8000",
                "time-server:latest",
            ],
            check=True,
        )
        print("✅ Container started successfully")
        print("🌐 Application available at http://localhost:8000")
    except subprocess.CalledProcessError as e:
        print(f"❌ Container start failed: {e}")
        sys.exit(1)


def stop_container():
    """Stop Docker container."""
    print("🐳 Stopping Docker container...")
    try:
        subprocess.run(["docker", "stop", "time-server-container"], check=True)
        subprocess.run(["docker", "rm", "time-server-container"], check=True)
        print("✅ Container stopped and removed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Container stop failed: {e}")
        sys.exit(1)


def show_logs():
    """Show Docker container logs."""
    print("🐳 Showing container logs...")
    try:
        subprocess.run(["docker", "logs", "-f", "time-server-container"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to show logs: {e}")
        sys.exit(1)


def docker_compose_up():
    """Start services with docker-compose."""
    print("🐳 Starting services with docker-compose...")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Services started successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker-compose failed: {e}")
        sys.exit(1)


def docker_compose_down():
    """Stop services with docker-compose."""
    print("🐳 Stopping services with docker-compose...")
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        print("✅ Services stopped successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker-compose failed: {e}")
        sys.exit(1)

# Time Server - Poetry Scripts

This project uses Poetry scripts for task management, similar to Gradle tasks.

## Setup

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Activate virtual environment**:
   ```bash
   poetry shell
   ```

## Available Tasks

### Development Tasks
```bash
poetry run dev-server    # Start Django development server
poetry run test          # Run test suite
poetry run test-cov      # Run tests with coverage reporting
poetry run lint          # Run code linting (flake8 + isort check)
poetry run format        # Format code (black + isort)
poetry run clean         # Clean project artifacts
```

### Docker Tasks
```bash
poetry run docker-build  # Build Docker image
poetry run docker-run    # Run Docker container
poetry run docker-stop   # Stop Docker container
poetry run docker-logs   # Show container logs
```

### Database Tasks
```bash
poetry run db-migrate    # Run Django migrations
poetry run db-reset      # Reset database (destructive!)
poetry run db-seed       # Seed database with sample data
```

### Deployment Tasks
```bash
poetry run deploy-staging # Deploy to staging environment
poetry run deploy-prod    # Deploy to production environment
```

## Usage Examples

```bash
# Start development
poetry run dev-server

# Run tests with coverage
poetry run test-cov

# Build and run Docker
poetry run docker-build
poetry run docker-run

# Format code before commit
poetry run format

# Deploy to staging
poetry run deploy-staging
```

## Gradle Comparison

| Gradle | Poetry |
|--------|--------|
| `./gradlew build` | `poetry run test` |
| `./gradlew test` | `poetry run test` |
| `./gradlew clean` | `poetry run clean` |
| `./gradlew dockerBuild` | `poetry run docker-build` |

## Adding New Tasks

To add a new task:

1. Add the function to the appropriate script file in `scripts/`
2. Add the script entry to `pyproject.toml` under `[tool.poetry.scripts]`
3. Run `poetry install` to register the new script

Example:
```toml
[tool.poetry.scripts]
my-task = "scripts.my_module:my_function"
```

Then use: `poetry run my-task`



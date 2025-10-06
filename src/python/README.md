# Time Server

A Django REST API server for time-related operations.

## Development Setup

1. Install Poetry if not already installed
2. Install dependencies: `poetry install`
3. Run migrations: `poetry run python manage.py migrate`
4. Start development server: `poetry run python manage.py runserver`

## Code Quality

- Format code: `poetry run black .`
- Sort imports: `poetry run isort .`
- Lint code: `poetry run flake8 .`
- Run tests: `poetry run pytest`


## quick start commands
```cd /home/tcronin/src/time_server/src/python```

-  Install dependencies
  - ```./dev.sh install```
- Run migrations
  - ```./dev.sh migrate```
- Start development server
  - ```./dev.sh runserver```
- api examples
  - ```curl http://localhost:8000/api/time/```
  - ```curl http://localhost:8000/api/health/```
- Run tests
  - ```./dev.sh test```
- Format code
  - ```./dev.sh format```
- Run linting
  - ```./dev.sh lint```

## docs
- [project structure](docs/PROJECT_STRUCTURE.md)
- [rest api](docs/REST_API_DOCUMENTATION.md)
- [api usage](docs/API_USAGE_EXAMPLES.md)
- [renogy](docs/RENOGY_MODULE_DOCUMENTATION.md)
- [time server rest api](docs/SWAGGER_UI_DOCUMENTATION.md)

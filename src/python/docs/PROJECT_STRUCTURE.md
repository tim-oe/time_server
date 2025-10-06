# Time Server Project Structure

## Overview

The Time Server project has been reorganized into a modular, scalable structure that separates concerns and makes the codebase more maintainable. This document explains the new organization and its benefits.

## Directory Structure

```
src/python/
├── apps/                          # Application modules
│   ├── common/                    # Shared utilities and components
│   │   ├── models/               # Common models
│   │   ├── views/                # Common views and utilities
│   │   ├── serializers/          # Common serializers
│   │   └── utils/                # Common utilities
│   ├── time_management/          # Time tracking functionality
│   │   ├── models.py            # TimeEntry model
│   │   ├── views.py             # Time management views
│   │   ├── serializers.py       # Time management serializers
│   │   ├── urls.py              # Time management URLs
│   │   └── apps.py              # App configuration
│   ├── renogy_devices/          # Renogy device management
│   │   ├── device.py            # Renogy device classes
│   │   ├── views.py             # Renogy device views
│   │   ├── urls.py              # Renogy device URLs
│   │   └── apps.py              # App configuration
│   └── ds18b20_sensors/         # DS18B20 temperature sensors
│       ├── sensor.py            # DS18B20 sensor classes
│       ├── views.py             # DS18B20 sensor views
│       ├── urls.py              # DS18B20 sensor URLs
│       └── apps.py              # App configuration
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   │   ├── test_time_management.py
│   │   ├── test_renogy.py
│   │   └── test_ds18b20.py
│   └── integration/             # Integration tests
├── api/                         # Main API configuration
│   └── urls.py                  # Main URL routing
├── time_server/                 # Django project settings
│   ├── settings.py              # Django configuration
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
├── docs/                        # Documentation
├── reports/                     # Test and coverage reports
│   ├── htmlcov/                # HTML coverage reports
│   ├── coverage.xml            # XML coverage report
│   └── .coverage               # Coverage data file
├── manage.py                    # Django management script
├── pyproject.toml              # Poetry configuration
└── README.md                   # Project documentation
```

## Benefits of the New Structure

### 1. **Separation of Concerns**
- Each app has a single responsibility
- Time management, device monitoring, and sensor reading are isolated
- Common functionality is shared through the `common` package

### 2. **Scalability**
- Easy to add new apps without affecting existing code
- Each app can be developed and tested independently
- Clear boundaries between different functionalities

### 3. **Maintainability**
- Related code is grouped together
- Easy to locate and modify specific functionality
- Reduced coupling between different parts of the system

### 4. **Testability**
- Tests are organized by functionality
- Unit tests are separated from integration tests
- Each app can be tested in isolation

### 5. **Reusability**
- Common utilities can be shared across apps
- Apps can be easily extracted into separate packages
- Clear interfaces between components

## App Descriptions

### Time Management App (`apps/time_management/`)
**Purpose**: Handles time tracking and timer functionality

**Components**:
- `models.py`: TimeEntry model for storing time entries
- `views.py`: API views for time management operations
- `serializers.py`: Data serialization for time entries
- `urls.py`: URL routing for time management endpoints

**Key Features**:
- Create, read, update, delete time entries
- Start/stop timers
- Get active timers
- Time entry statistics
- Validation for time entries

### Renogy Devices App (`apps/renogy_devices/`)
**Purpose**: Manages Renogy Bluetooth devices and data reading

**Components**:
- `device.py`: RenogyDevice and RenogyDeviceManager classes
- `views.py`: API views for device management
- `urls.py`: URL routing for device endpoints

**Key Features**:
- Add/remove devices
- Connect/disconnect from devices
- Read device data (battery, PV, load information)
- Device status monitoring
- Mock data for testing

### DS18B20 Sensors App (`apps/ds18b20_sensors/`)
**Purpose**: Handles DS18B20 temperature sensor reading via 1-Wire interface

**Components**:
- `sensor.py`: DS18B20Sensor and DS18B20SensorManager classes
- `views.py`: API views for sensor management
- `urls.py`: URL routing for sensor endpoints

**Key Features**:
- Add/remove sensors
- Read temperature data
- Sensor discovery
- Temperature conversion (Celsius/Fahrenheit)
- Error handling and validation

### Common Package (`apps/common/`)
**Purpose**: Shared utilities and components used across apps

**Components**:
- `models/`: Common model base classes
- `views/`: Common view utilities and documentation
- `serializers/`: Common serializer base classes
- `utils/`: Shared utility functions

## URL Structure

The API endpoints are organized as follows:

```
/api/
├── time/                        # Time management
│   ├── time-entries/           # Time entry CRUD
│   ├── time-entries/statistics/ # Time statistics
│   ├── time-entries/start_timer/ # Start timer
│   └── time-entries/{id}/stop_timer/ # Stop timer
├── renogy/                     # Renogy devices
│   ├── devices/                # Device management
│   ├── devices/{address}/connect/ # Connect to device
│   ├── devices/{address}/data/ # Get device data
│   └── connect-all/            # Connect all devices
├── ds18b20/                    # DS18B20 sensors
│   ├── sensors/                # Sensor management
│   ├── sensors/{id}/temperature/ # Get temperature
│   ├── discover/               # Discover sensors
│   └── all-temperatures/       # Get all temperatures
└── docs/                       # Documentation
    ├── swagger-ui/             # Swagger UI
    ├── redoc/                  # ReDoc
    └── schema/                 # OpenAPI schema
```

## Testing Structure

### Unit Tests (`tests/unit/`)
- `test_time_management.py`: Tests for time management functionality
- `test_renogy.py`: Tests for Renogy device functionality
- `test_ds18b20.py`: Tests for DS18B20 sensor functionality

### Integration Tests (`tests/integration/`)
- End-to-end API tests
- Cross-app integration tests
- Performance tests

## Configuration

### Django Settings (`time_server/settings.py`)
The settings file includes all apps in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    # Custom apps
    "apps.time_management",
    "apps.renogy_devices",
    "apps.ds18b20_sensors",
    "api",
]
```

### Poetry Configuration (`pyproject.toml`)
Dependencies are managed through Poetry with proper version constraints and development dependencies.

## Migration from Old Structure

The old structure had everything in the `api/` directory. The new structure:

1. **Moved models**: `api/models.py` → `apps/time_management/models.py`
2. **Moved views**: `api/views.py` → `apps/time_management/views.py`
3. **Moved serializers**: `api/serializers.py` → `apps/time_management/serializers.py`
4. **Split device code**: `api/renogy_device.py` → `apps/renogy_devices/device.py`
5. **Split sensor code**: `api/ds18b20_sensor.py` → `apps/ds18b20_sensors/sensor.py`
6. **Organized tests**: `api/tests.py` → `tests/unit/test_time_management.py`
7. **Created common utilities**: `apps/common/` for shared functionality

## Development Workflow

### Adding a New App
1. Create directory under `apps/`
2. Add `__init__.py`, `apps.py`, and other necessary files
3. Add to `INSTALLED_APPS` in settings
4. Create URL routing
5. Add tests in `tests/unit/`

### Adding New Functionality
1. Identify which app the functionality belongs to
2. Add models, views, serializers as needed
3. Update URL routing
4. Add comprehensive tests
5. Update documentation

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific app tests
poetry run pytest tests/unit/test_time_management.py

# Run with coverage (reports go to reports/ folder)
poetry run pytest --cov=apps --cov=api

# View coverage report
open reports/htmlcov/index.html
```

## Best Practices

1. **Keep apps focused**: Each app should have a single responsibility
2. **Use common utilities**: Share code through the `common` package
3. **Write comprehensive tests**: Each app should have thorough test coverage
4. **Document APIs**: Use `drf-spectacular` for API documentation
5. **Follow Django conventions**: Use Django's app structure and naming conventions
6. **Maintain clean interfaces**: Keep clear boundaries between apps

## Future Enhancements

The new structure makes it easy to:

1. **Add new device types**: Create new apps for different device protocols
2. **Implement microservices**: Extract apps into separate services
3. **Add new features**: Extend existing apps or create new ones
4. **Improve testing**: Add more comprehensive test suites
5. **Enhance documentation**: Add more detailed API documentation

This modular structure provides a solid foundation for scaling the Time Server project while maintaining code quality and developer productivity.

# API Usage Examples

This document provides practical examples of how to use the Time Server REST API.

## Base URL
```
http://localhost:8000/api/
```

## Available Endpoints

### 1. Current Time
**GET** `/api/time/`

Returns the current server time and timezone information.

**Example Request:**
```bash
curl http://localhost:8000/api/time/
```

**Example Response:**
```json
{
    "current_time": "2024-01-15T10:30:45.123456Z",
    "timezone": "UTC",
    "unix_timestamp": 1705312245.123456
}
```

### 2. Health Check
**GET** `/api/health/`

Returns the health status of the API.

**Example Request:**
```bash
curl http://localhost:8000/api/health/
```

**Example Response:**
```json
{
    "status": "healthy"
}
```

### 3. Time Entries

#### List Time Entries
**GET** `/api/time-entries/`

Returns a paginated list of all time entries.

**Example Request:**
```bash
curl http://localhost:8000/api/time-entries/
```

**Example Response:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "description": "Working on project",
            "start_time": "2024-01-15T09:00:00Z",
            "end_time": "2024-01-15T11:00:00Z",
            "duration": "2:00:00",
            "created_at": "2024-01-15T09:00:00Z",
            "updated_at": "2024-01-15T11:00:00Z"
        }
    ]
}
```

#### Create Time Entry
**POST** `/api/time-entries/`

Creates a new time entry.

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/time-entries/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Meeting with client",
    "start_time": "2024-01-15T14:00:00Z",
    "end_time": "2024-01-15T15:30:00Z"
  }'
```

**Example Response:**
```json
{
    "id": 2,
    "description": "Meeting with client",
    "start_time": "2024-01-15T14:00:00Z",
    "end_time": "2024-01-15T15:30:00Z",
    "duration": "1:30:00",
    "created_at": "2024-01-15T14:00:00Z",
    "updated_at": "2024-01-15T14:00:00Z"
}
```

#### Get Time Entry Detail
**GET** `/api/time-entries/{id}/`

Returns details of a specific time entry.

**Example Request:**
```bash
curl http://localhost:8000/api/time-entries/1/
```

#### Update Time Entry
**PUT** `/api/time-entries/{id}/` or **PATCH** `/api/time-entries/{id}/`

Updates an existing time entry.

**Example Request:**
```bash
curl -X PATCH http://localhost:8000/api/time-entries/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description"
  }'
```

#### Delete Time Entry
**DELETE** `/api/time-entries/{id}/`

Deletes a time entry.

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/time-entries/1/
```

### 4. Timer Operations

#### Start Timer
**POST** `/api/time-entries/start_timer/`

Starts a new timer (creates a time entry without end time).

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/time-entries/start_timer/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Working on new feature",
    "start_time": "2024-01-15T16:00:00Z"
  }'
```

**Example Response:**
```json
{
    "id": 3,
    "description": "Working on new feature",
    "start_time": "2024-01-15T16:00:00Z",
    "end_time": null,
    "duration": null,
    "created_at": "2024-01-15T16:00:00Z",
    "updated_at": "2024-01-15T16:00:00Z"
}
```

#### Stop Timer
**POST** `/api/time-entries/{id}/stop_timer/`

Stops a running timer by setting the end time.

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/time-entries/3/stop_timer/
```

**Example Response:**
```json
{
    "id": 3,
    "description": "Working on new feature",
    "start_time": "2024-01-15T16:00:00Z",
    "end_time": "2024-01-15T17:30:00Z",
    "duration": "1:30:00",
    "created_at": "2024-01-15T16:00:00Z",
    "updated_at": "2024-01-15T17:30:00Z"
}
```

#### Get Active Timers
**GET** `/api/time-entries/active_timers/`

Returns all currently running timers (time entries without end time).

**Example Request:**
```bash
curl http://localhost:8000/api/time-entries/active_timers/
```

**Example Response:**
```json
[
    {
        "id": 4,
        "description": "Current task",
        "start_time": "2024-01-15T18:00:00Z",
        "end_time": null,
        "duration": null,
        "created_at": "2024-01-15T18:00:00Z",
        "updated_at": "2024-01-15T18:00:00Z"
    }
]
```

#### Get Statistics
**GET** `/api/time-entries/statistics/`

Returns statistics about all time entries.

**Example Request:**
```bash
curl http://localhost:8000/api/time-entries/statistics/
```

**Example Response:**
```json
{
    "total_entries": 5,
    "total_duration": "8:45:30",
    "total_seconds": 31530.0
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

### 400 Bad Request
```json
{
    "start_time": ["Start time cannot be in the future"],
    "non_field_errors": ["End time must be after start time"]
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "detail": "A server error occurred."
}
```

## Authentication

Currently, the API allows anonymous access. For production use, consider implementing authentication:

```python
# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Rate Limiting

For production deployments, consider implementing rate limiting:

```python
# Install django-ratelimit
pip install django-ratelimit

# In views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
def create_time_entry(request):
    # Your view logic
    pass
```

## CORS Configuration

The API is configured to allow CORS requests from localhost:

```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

## Testing the API

You can test the API using various tools:

### Using curl
```bash
# Test all endpoints
curl http://localhost:8000/api/time/
curl http://localhost:8000/api/health/
curl http://localhost:8000/api/time-entries/
```

### Using Python requests
```python
import requests

# Get current time
response = requests.get('http://localhost:8000/api/time/')
print(response.json())

# Create a time entry
data = {
    'description': 'Test entry',
    'start_time': '2024-01-15T10:00:00Z',
    'end_time': '2024-01-15T11:00:00Z'
}
response = requests.post('http://localhost:8000/api/time-entries/', json=data)
print(response.json())
```

### Using Postman
1. Import the collection or manually create requests
2. Set base URL to `http://localhost:8000/api/`
3. Test all endpoints with appropriate HTTP methods

## Deployment Considerations

### Production Settings
```python
# In settings.py for production
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-secret-key'

# Use a production database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'time_server',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### WSGI Deployment
```bash
# Using Gunicorn
gunicorn time_server.wsgi:application --bind 0.0.0.0:8000

# Using uWSGI
uwsgi --module time_server.wsgi:application --http :8000
```

### ASGI Deployment
```bash
# Using Uvicorn
uvicorn time_server.asgi:application --host 0.0.0.0 --port 8000

# Using Daphne
daphne -b 0.0.0.0 -p 8000 time_server.asgi:application
```

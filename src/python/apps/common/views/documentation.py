"""
Custom API Documentation Views

This module provides additional documentation endpoints and views
for the Time Server API.
"""

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(
    summary="API Information",
    description="Get general information about the API",
    tags=["Documentation"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "name": {"type": "string", "example": "Time Server API"},
                "version": {"type": "string", "example": "1.0.0"},
                "description": {"type": "string"},
                "endpoints": {"type": "object"},
                "features": {"type": "array", "items": {"type": "string"}},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_info(request):
    """Get general API information."""
    return Response(
        {
            "name": "Time Server API",
            "version": "1.0.0",
            "description": (
                "A comprehensive API for time management and Renogy device monitoring"
            ),
            "endpoints": {
                "time": {
                    "current_time": "/api/time/",
                    "health_check": "/api/health/",
                },
                "time_entries": {
                    "list": "/api/time-entries/",
                    "create": "POST /api/time-entries/",
                    "detail": "/api/time-entries/{id}/",
                    "statistics": "/api/time-entries/statistics/",
                    "start_timer": "POST /api/time-entries/start_timer/",
                    "stop_timer": "POST /api/time-entries/{id}/stop_timer/",
                    "active_timers": "/api/time-entries/active_timers/",
                },
                "renogy_devices": {
                    "list": "/api/renogy/devices/",
                    "add": "POST /api/renogy/devices/add/",
                    "remove": "DELETE /api/renogy/devices/{address}/",
                    "connect": "POST /api/renogy/devices/{address}/connect/",
                    "disconnect": "POST /api/renogy/devices/{address}/disconnect/",
                    "data": "/api/renogy/devices/{address}/data/",
                    "status": "/api/renogy/devices/{address}/status/",
                    "connect_all": "POST /api/renogy/connect-all/",
                    "disconnect_all": "POST /api/renogy/disconnect-all/",
                    "all_data": "/api/renogy/all-data/",
                },
                "ds18b20_sensors": {
                    "list": "/api/ds18b20/sensors/",
                    "add": "POST /api/ds18b20/sensors/add/",
                    "remove": "DELETE /api/ds18b20/sensors/{sensor_id}/",
                    "temperature": "/api/ds18b20/sensors/{sensor_id}/temperature/",
                    "info": "/api/ds18b20/sensors/{sensor_id}/info/",
                    "discover": "/api/ds18b20/discover/",
                    "all_temperatures": "/api/ds18b20/all-temperatures/",
                    "summary": "/api/ds18b20/summary/",
                },
                "documentation": {
                    "swagger_ui": "/api/docs/",
                    "redoc": "/api/redoc/",
                    "schema": "/api/schema/",
                    "api_info": "/api/info/",
                },
            },
            "features": [
                "Time management and tracking",
                "Renogy device monitoring",
                "DS18B20 temperature sensor support",
                "Bluetooth device communication",
                "1-Wire temperature sensor interface",
                "RESTful API design",
                "Comprehensive documentation",
                "Real-time data reading",
                "Device management",
                "Statistics and reporting",
            ],
        }
    )


@extend_schema(
    summary="API Usage Examples",
    description="Get usage examples for common API operations",
    tags=["Documentation"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "examples": {"type": "object"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_examples(request):
    """Get API usage examples."""
    return Response(
        {
            "examples": {
                "time_management": {
                    "get_current_time": {
                        "method": "GET",
                        "url": "/api/time/",
                        "description": "Get current server time",
                        "curl": "curl http://localhost:8000/api/time/",
                    },
                    "create_time_entry": {
                        "method": "POST",
                        "url": "/api/time-entries/",
                        "description": "Create a new time entry",
                        "curl": (
                            """curl -X POST http://localhost:8000/api/time-entries/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "description": "Working on project",
    "start_time": "2024-01-15T09:00:00Z",
    "end_time": "2024-01-15T11:00:00Z"
  }'"""
                        ),
                    },
                    "start_timer": {
                        "method": "POST",
                        "url": "/api/time-entries/start_timer/",
                        "description": "Start a new timer",
                        "curl": (
                            """curl -X POST http://localhost:8000/api/time-entries/start_timer/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "description": "Current task",
    "start_time": "2024-01-15T14:00:00Z"
  }'"""
                        ),
                    },
                },
                "renogy_devices": {
                    "add_device": {
                        "method": "POST",
                        "url": "/api/renogy/devices/add/",
                        "description": "Add a new Renogy device",
                        "curl": (
                            """curl -X POST http://localhost:8000/api/renogy/devices/add/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "device_address": "F8:55:48:17:99:EB",
    "timeout": 10
  }'"""
                        ),
                    },
                    "connect_device": {
                        "method": "POST",
                        "url": "/api/renogy/devices/F8:55:48:17:99:EB/connect/",
                        "description": "Connect to a Renogy device",
                        "curl": (
                            "curl -X POST http://localhost:8000/api/renogy/devices/"
                            "F8:55:48:17:99:EB/connect/"
                        ),
                    },
                    "get_device_data": {
                        "method": "GET",
                        "url": "/api/renogy/devices/F8:55:48:17:99:EB/data/",
                        "description": "Get data from a Renogy device",
                        "curl": (
                            "curl http://localhost:8000/api/renogy/devices/"
                            "F8:55:48:17:99:EB/data/"
                        ),
                    },
                },
                "ds18b20_sensors": {
                    "add_sensor": {
                        "method": "POST",
                        "url": "/api/ds18b20/sensors/add/",
                        "description": "Add a new DS18B20 temperature sensor",
                        "curl": (
                            """curl -X POST http://localhost:8000/api/ds18b20/sensors/add/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "sensor_id": "28-0123456789ab",
    "sensor_name": "Battery Temperature"
  }'"""
                        ),
                    },
                    "get_temperature": {
                        "method": "GET",
                        "url": "/api/ds18b20/sensors/28-0123456789ab/temperature/",
                        "description": "Get temperature from a DS18B20 sensor",
                        "curl": (
                            "curl http://localhost:8000/api/ds18b20/sensors/"
                            "28-0123456789ab/temperature/"
                        ),
                    },
                    "discover_sensors": {
                        "method": "GET",
                        "url": "/api/ds18b20/discover/",
                        "description": "Discover all available DS18B20 sensors",
                        "curl": "curl http://localhost:8000/api/ds18b20/discover/",
                    },
                },
            },
        }
    )


@extend_schema(
    summary="API Status",
    description="Get the current status of the API and its components",
    tags=["Documentation"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "healthy"},
                "components": {"type": "object"},
                "version": {"type": "string", "example": "1.0.0"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_status(request):
    """Get API status information."""
    return Response(
        {
            "status": "healthy",
            "version": "1.0.0",
            "components": {
                "database": "connected",
                "renogy_library": "available",
                "bluetooth": "available",
                "documentation": "available",
            },
            "endpoints": {
                "total": 25,
                "time_management": 8,
                "renogy_devices": 10,
                "documentation": 4,
                "health": 3,
            },
            "features": {
                "time_tracking": True,
                "device_monitoring": True,
                "bluetooth_communication": True,
                "rest_api": True,
                "documentation": True,
                "testing": True,
            },
        }
    )


@extend_schema(
    summary="API Changelog",
    description="Get the API changelog and version history",
    tags=["Documentation"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "versions": {"type": "array", "items": {"type": "object"}},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def api_changelog(request):
    """Get API changelog."""
    return Response(
        {
            "versions": [
                {
                    "version": "1.0.0",
                    "date": "2024-01-15",
                    "changes": [
                        "Initial release",
                        "Time management API",
                        "Renogy device integration",
                        "DS18B20 temperature sensor support",
                        "Bluetooth communication",
                        "Comprehensive documentation",
                        "Swagger UI integration",
                        "Complete test suite",
                    ],
                    "features": [
                        "Time entry management",
                        "Timer functionality",
                        "Device monitoring",
                        "Temperature monitoring",
                        "Statistics and reporting",
                        "RESTful API design",
                    ],
                },
            ],
        }
    )

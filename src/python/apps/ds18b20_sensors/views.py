"""
DS18B20 Temperature Sensor API Views

This module provides REST API endpoints for interacting with DS18B20 temperature sensors.
"""

import asyncio

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .sensor import (
    DS18B20Sensor,
    DS18B20SensorManager,
    TemperatureReading,
    discover_all_ds18b20_sensors,
)

# Global sensor manager instance
sensor_manager = DS18B20SensorManager()


@extend_schema(
    summary="List DS18B20 sensors",
    description="Retrieve a list of all managed DS18B20 temperature sensors",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "sensors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sensor_id": {
                                "type": "string",
                                "example": "28-0123456789ab",
                            },
                            "sensor_name": {
                                "type": "string",
                                "example": "Battery Temperature",
                            },
                            "is_available": {"type": "boolean", "example": True},
                            "device_path": {"type": "string"},
                        },
                    },
                },
                "total_count": {"type": "integer", "example": 2},
            },
        }
    },
)
@api_view(["GET"])
def ds18b20_sensor_list(request):
    """List all managed DS18B20 sensors."""
    sensors = sensor_manager.list_sensors()
    return Response({"sensors": sensors, "total_count": len(sensors)})


@extend_schema(
    summary="Add DS18B20 sensor",
    description="Add a new DS18B20 temperature sensor to the manager",
    tags=["DS18B20 Sensors"],
    request={
        "type": "object",
        "properties": {
            "sensor_id": {"type": "string", "example": "28-0123456789ab"},
            "sensor_name": {"type": "string", "example": "Battery Temperature"},
        },
        "required": ["sensor_id", "sensor_name"],
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Sensor added successfully"},
                "sensor_id": {"type": "string", "example": "28-0123456789ab"},
                "sensor_name": {"type": "string", "example": "Battery Temperature"},
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "sensor_id is required"},
            },
        },
        409: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Sensor already exists"},
            },
        },
    },
)
@api_view(["POST"])
def ds18b20_sensor_add(request):
    """Add a new DS18B20 sensor."""
    sensor_id = request.data.get("sensor_id")
    sensor_name = request.data.get("sensor_name")

    if not sensor_id:
        return Response(
            {"error": "sensor_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not sensor_name:
        return Response(
            {"error": "sensor_name is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Check if sensor already exists
    if sensor_manager.get_sensor(sensor_id):
        return Response(
            {"error": "Sensor already exists"}, status=status.HTTP_409_CONFLICT
        )

    # Add sensor
    sensor = sensor_manager.add_sensor(sensor_id, sensor_name)

    return Response(
        {
            "message": "Sensor added successfully",
            "sensor_id": sensor.sensor_id,
            "sensor_name": sensor.sensor_name,
            "is_available": sensor.is_available(),
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    summary="Remove DS18B20 sensor",
    description="Remove a DS18B20 sensor from the manager",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Sensor removed successfully"},
                "sensor_id": {"type": "string", "example": "28-0123456789ab"},
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Sensor not found"},
            },
        },
    },
)
@api_view(["DELETE"])
def ds18b20_sensor_remove(request, sensor_id):
    """Remove a DS18B20 sensor."""
    if not sensor_manager.get_sensor(sensor_id):
        return Response({"error": "Sensor not found"}, status=status.HTTP_404_NOT_FOUND)

    sensor_manager.remove_sensor(sensor_id)

    return Response({"message": "Sensor removed successfully", "sensor_id": sensor_id})


@extend_schema(
    summary="Get sensor temperature",
    description="Read temperature from a specific DS18B20 sensor",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "sensor_id": {"type": "string", "example": "28-0123456789ab"},
                "sensor_name": {"type": "string", "example": "Battery Temperature"},
                "temperature_celsius": {"type": "number", "example": 25.5},
                "temperature_fahrenheit": {"type": "number", "example": 77.9},
                "timestamp": {"type": "string", "format": "date-time"},
                "is_valid": {"type": "boolean", "example": True},
                "error_message": {"type": "string", "nullable": True},
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Sensor not found"},
            },
        },
    },
)
@api_view(["GET"])
def ds18b20_sensor_temperature(request, sensor_id):
    """Get temperature from a specific DS18B20 sensor."""
    sensor = sensor_manager.get_sensor(sensor_id)
    if not sensor:
        return Response({"error": "Sensor not found"}, status=status.HTTP_404_NOT_FOUND)

    # Read temperature
    reading = sensor.read_temperature()
    return Response(reading.to_dict())


@extend_schema(
    summary="Get sensor information",
    description="Get information about a specific DS18B20 sensor",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "sensor_id": {"type": "string", "example": "28-0123456789ab"},
                "sensor_name": {"type": "string", "example": "Battery Temperature"},
                "device_path": {"type": "string"},
                "is_available": {"type": "boolean", "example": True},
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Sensor not found"},
            },
        },
    },
)
@api_view(["GET"])
def ds18b20_sensor_info(request, sensor_id):
    """Get information about a specific DS18B20 sensor."""
    sensor = sensor_manager.get_sensor(sensor_id)
    if not sensor:
        return Response({"error": "Sensor not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(sensor.get_sensor_info())


@extend_schema(
    summary="Discover DS18B20 sensors",
    description="Discover all available DS18B20 sensors on the system",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "sensor_ids": {
                    "type": "array",
                    "items": {"type": "string", "example": "28-0123456789ab"},
                },
                "count": {"type": "integer", "example": 2},
            },
        }
    },
)
@api_view(["GET"])
def ds18b20_discover_sensors(request):
    """Discover all available DS18B20 sensors."""
    sensor_ids = discover_all_ds18b20_sensors()
    return Response({"sensor_ids": sensor_ids, "count": len(sensor_ids)})


@extend_schema(
    summary="Get all sensor temperatures",
    description="Read temperature from all managed DS18B20 sensors",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "readings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sensor_id": {"type": "string"},
                            "sensor_name": {"type": "string"},
                            "temperature_celsius": {"type": "number"},
                            "temperature_fahrenheit": {"type": "number"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "is_valid": {"type": "boolean"},
                            "error_message": {"type": "string", "nullable": True},
                        },
                    },
                },
                "total_sensors": {"type": "integer", "example": 2},
                "valid_readings": {"type": "integer", "example": 2},
            },
        }
    },
)
@api_view(["GET"])
def ds18b20_all_temperatures(request):
    """Get temperature from all managed sensors."""
    readings = sensor_manager.read_all_temperatures()
    valid_readings = sum(1 for reading in readings if reading.is_valid)

    return Response(
        {
            "readings": [reading.to_dict() for reading in readings],
            "total_sensors": len(readings),
            "valid_readings": valid_readings,
        }
    )


@extend_schema(
    summary="Get sensor summary",
    description="Get a summary of all managed sensors and their status",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "total_sensors": {"type": "integer", "example": 2},
                "available_sensors": {"type": "integer", "example": 2},
                "unavailable_sensors": {"type": "integer", "example": 0},
                "sensors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sensor_id": {"type": "string"},
                            "sensor_name": {"type": "string"},
                            "is_available": {"type": "boolean"},
                        },
                    },
                },
            },
        }
    },
)
@api_view(["GET"])
def ds18b20_sensor_summary(request):
    """Get summary of all sensors."""
    summary = sensor_manager.get_sensor_summary()
    return Response(summary)


@extend_schema_view(
    list=extend_schema(
        summary="List DS18B20 sensors",
        description="Retrieve a list of all managed DS18B20 sensors",
        tags=["DS18B20 Sensors"],
    ),
    create=extend_schema(
        summary="Add DS18B20 sensor",
        description="Add a new DS18B20 sensor to the manager",
        tags=["DS18B20 Sensors"],
    ),
    destroy=extend_schema(
        summary="Remove DS18B20 sensor",
        description="Remove a DS18B20 sensor from the manager",
        tags=["DS18B20 Sensors"],
    ),
)
class DS18B20SensorViewSet(viewsets.ViewSet):
    """ViewSet for DS18B20 sensor operations."""

    permission_classes = [AllowAny]

    def list(self, request):
        """List all sensors."""
        return ds18b20_sensor_list(request)

    def create(self, request):
        """Add a new sensor."""
        return ds18b20_sensor_add(request)

    def destroy(self, request, pk=None):
        """Remove a sensor."""
        return ds18b20_sensor_remove(request, pk)

    @action(detail=True, methods=["get"])
    def temperature(self, request, pk=None):
        """Get sensor temperature."""
        return ds18b20_sensor_temperature(request, pk)

    @action(detail=True, methods=["get"])
    def info(self, request, pk=None):
        """Get sensor information."""
        return ds18b20_sensor_info(request, pk)

    @action(detail=False, methods=["get"])
    def discover(self, request):
        """Discover available sensors."""
        return ds18b20_discover_sensors(request)

    @action(detail=False, methods=["get"])
    def all_temperatures(self, request):
        """Get temperatures from all sensors."""
        return ds18b20_all_temperatures(request)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get sensor summary."""
        return ds18b20_sensor_summary(request)

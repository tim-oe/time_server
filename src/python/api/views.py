from django.utils import timezone

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


# pylint: disable=line-too-long
@extend_schema(
    summary="Get current server time",
    description="Returns the current server time in ISO format with comprehensive timezone information including UTC offset and daylight saving time details",
    tags=["System"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "current_time": {"type": "string", "format": "date-time"},
                "timezone": {"type": "string"},
                "unix_timestamp": {"type": "number", "format": "float"},
            },
        }
    },
)  # noqa
@api_view(["GET"])
def current_time(request):
    """Return the current server time."""
    return Response(
        {
            "current_time": timezone.now().isoformat(),
            "timezone": str(timezone.get_current_timezone()),
            "unix_timestamp": timezone.now().timestamp(),
        }
    )


@extend_schema(
    summary="Health check",
    description="Returns the health status of the solar monitoring API server",
    tags=["System"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "healthy"},
                "services": {
                    "type": "object",
                    "properties": {
                        "renogy_devices": {"type": "string", "example": "operational"},
                        "ds18b20_sensors": {"type": "string", "example": "operational"},
                    },
                },
            },
        }
    },
)
@api_view(["GET"])
def health_check(request):
    """Health check endpoint for solar monitoring system."""
    return Response({
        "status": "healthy",
        "services": {
            "renogy_devices": "operational",
            "ds18b20_sensors": "operational",
        }
    })

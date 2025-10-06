from django.db.models import Count, Sum
from django.utils import timezone

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import TimeEntry
from .serializers import (
    TimeEntryCreateSerializer,
    TimeEntrySerializer,
    TimeEntryUpdateSerializer,
)


@extend_schema(
    summary="Get current server time",
    description="Returns the current server time in ISO format with timezone information",
    tags=["Time"],
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
)
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
    description="Returns the health status of the API server",
    tags=["Health"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "healthy"},
            },
        }
    },
)
@api_view(["GET"])
def health_check(request):
    """Health check endpoint."""
    return Response({"status": "healthy"})


@extend_schema_view(
    list=extend_schema(
        summary="List time entries",
        description="Retrieve a paginated list of all time entries",
        tags=["Time Entries"],
    ),
    create=extend_schema(
        summary="Create time entry",
        description="Create a new time entry with validation",
        tags=["Time Entries"],
    ),
    retrieve=extend_schema(
        summary="Get time entry",
        description="Retrieve a specific time entry by ID",
        tags=["Time Entries"],
    ),
    update=extend_schema(
        summary="Update time entry",
        description="Update an existing time entry (full update)",
        tags=["Time Entries"],
    ),
    partial_update=extend_schema(
        summary="Partially update time entry",
        description="Partially update an existing time entry",
        tags=["Time Entries"],
    ),
    destroy=extend_schema(
        summary="Delete time entry",
        description="Delete a time entry by ID",
        tags=["Time Entries"],
    ),
)
class TimeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for time entries with advanced functionality."""

    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return TimeEntryCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TimeEntryUpdateSerializer
        return TimeEntrySerializer

    @extend_schema(
        summary="Get time entry statistics",
        description="Retrieve statistics about all time entries including total count and duration",
        tags=["Time Entries"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total_entries": {"type": "integer", "example": 10},
                    "total_duration": {"type": "string", "example": "25:30:15"},
                    "total_seconds": {"type": "number", "example": 91815.0},
                },
            }
        },
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get time entry statistics."""
        stats = TimeEntry.objects.aggregate(
            total_entries=Count("id"), total_duration=Sum("duration")
        )

        return Response(
            {
                "total_entries": stats["total_entries"],
                "total_duration": str(stats["total_duration"])
                if stats["total_duration"]
                else "0:00:00",
                "total_seconds": stats["total_duration"].total_seconds()
                if stats["total_duration"]
                else 0,
            }
        )

    @action(detail=True, methods=["post"])
    def stop_timer(self, request, pk=None):
        """Stop a running timer."""
        time_entry = self.get_object()

        if time_entry.end_time:
            return Response(
                {"error": "Timer already stopped"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        time_entry.end_time = timezone.now()
        time_entry.save()  # Duration is calculated in model's save method

        serializer = self.get_serializer(time_entry)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active_timers(self, request):
        """Get all active (running) timers."""
        active_timers = TimeEntry.objects.filter(end_time__isnull=True)
        serializer = self.get_serializer(active_timers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def start_timer(self, request):
        """Start a new timer."""
        serializer = TimeEntryCreateSerializer(data=request.data)

        if serializer.is_valid():
            time_entry = serializer.save(start_time=timezone.now())
            return Response(
                TimeEntrySerializer(time_entry).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

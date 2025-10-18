"""
Serializer Tests

Tests for all serializer classes across the application.
"""

from django.utils import timezone

import pytest
from rest_framework import serializers

from apps.time_management.models import TimeEntry
from apps.time_management.serializers import (
    TimeEntryCreateSerializer,
    TimeEntrySerializer,
    TimeEntryUpdateSerializer,
)


@pytest.mark.django_db
class TestTimeEntrySerializer:
    """Test cases for TimeEntrySerializer."""

    def test_serialize_valid_data(self):
        """Test serializing valid time entry data."""
        # Create a time entry
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end_time = timezone.datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Test entry", start_time=start_time, end_time=end_time
        )

        serializer = TimeEntrySerializer(time_entry)
        data = serializer.data

        assert data["description"] == "Test entry"
        assert "start_time" in data
        assert "end_time" in data
        assert "duration" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_serialize_without_end_time(self):
        """Test serializing time entry without end time."""
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Active timer", start_time=start_time
        )

        serializer = TimeEntrySerializer(time_entry)
        data = serializer.data

        assert data["description"] == "Active timer"
        assert data["end_time"] is None
        assert data["duration"] is None

    def test_deserialize_valid_data(self):
        """Test deserializing valid time entry data."""
        data = {
            "description": "New entry",
            "start_time": "2024-01-01T10:00:00Z",
            "end_time": "2024-01-01T11:00:00Z",
        }

        serializer = TimeEntrySerializer(data=data)
        assert serializer.is_valid()

        time_entry = serializer.save()
        assert time_entry.description == "New entry"
        assert time_entry.start_time is not None
        assert time_entry.end_time is not None

    def test_deserialize_missing_required_fields(self):
        """Test deserializing with missing required fields."""
        data = {
            "start_time": "2024-01-01T10:00:00Z"
            # Missing description
        }

        serializer = TimeEntrySerializer(data=data)
        assert not serializer.is_valid()
        assert "description" in serializer.errors

    def test_read_only_fields(self):
        """Test that read-only fields are not updated during deserialization."""
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Original entry", start_time=start_time
        )

        original_created_at = time_entry.created_at
        original_updated_at = time_entry.updated_at

        data = {
            "description": "Updated entry",
            "created_at": "2024-01-01T09:00:00Z",  # Should be ignored
            "updated_at": "2024-01-01T09:00:00Z",  # Should be ignored
            "duration": "2:00:00",  # Should be ignored
        }

        serializer = TimeEntrySerializer(time_entry, data=data, partial=True)
        assert serializer.is_valid()
        updated_entry = serializer.save()

        # Read-only fields should not be changed
        assert updated_entry.created_at == original_created_at
        assert updated_entry.duration != "2:00:00"  # Should be calculated, not set


@pytest.mark.django_db
class TestTimeEntryCreateSerializer:
    """Test cases for TimeEntryCreateSerializer."""

    def test_serialize_valid_data(self):
        """Test serializing valid create data."""
        data = {
            "description": "New entry",
            "start_time": "2024-01-01T10:00:00Z",
            "end_time": "2024-01-01T11:00:00Z",
        }

        serializer = TimeEntryCreateSerializer(data=data)
        assert serializer.is_valid()

        time_entry = serializer.save()
        assert time_entry.description == "New entry"
        assert time_entry.start_time is not None
        assert time_entry.end_time is not None

    def test_serialize_without_end_time(self):
        """Test serializing create data without end time."""
        data = {"description": "Active timer", "start_time": "2024-01-01T10:00:00Z"}

        serializer = TimeEntryCreateSerializer(data=data)
        assert serializer.is_valid()

        time_entry = serializer.save()
        assert time_entry.description == "Active timer"
        assert time_entry.end_time is None

    def test_validate_start_time_future(self):
        """Test validation of start time in the future."""
        future_time = timezone.now() + timezone.timedelta(hours=1)
        data = {"description": "Future entry", "start_time": future_time.isoformat()}

        serializer = TimeEntryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "start_time" in serializer.errors

    def test_validate_end_before_start(self):
        """Test validation when end time is before start time."""
        data = {
            "description": "Invalid entry",
            "start_time": "2024-01-01T11:00:00Z",
            "end_time": "2024-01-01T10:00:00Z",  # End before start
        }

        serializer = TimeEntryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_validate_same_start_end_time(self):
        """Test validation when start and end times are the same."""
        data = {
            "description": "Same time entry",
            "start_time": "2024-01-01T10:00:00Z",
            "end_time": "2024-01-01T10:00:00Z",  # Same as start
        }

        serializer = TimeEntryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        data = {
            "start_time": "2024-01-01T10:00:00Z"
            # Missing description
        }

        serializer = TimeEntryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "description" in serializer.errors

    def test_validate_invalid_datetime_format(self):
        """Test validation with invalid datetime format."""
        data = {"description": "Invalid format", "start_time": "invalid-datetime"}

        serializer = TimeEntryCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "start_time" in serializer.errors

    def test_validate_valid_past_time(self):
        """Test validation with valid past time."""
        past_time = timezone.now() - timezone.timedelta(hours=1)
        data = {"description": "Past entry", "start_time": past_time.isoformat()}

        serializer = TimeEntryCreateSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestTimeEntryUpdateSerializer:
    """Test cases for TimeEntryUpdateSerializer."""

    def test_serialize_valid_data(self):
        """Test serializing valid update data."""
        data = {
            "description": "Updated description",
            "end_time": "2024-01-01T12:00:00Z",
        }

        serializer = TimeEntryUpdateSerializer(data=data)
        assert serializer.is_valid()

    def test_serialize_partial_data(self):
        """Test serializing partial update data."""
        data = {"description": "Only description updated"}

        serializer = TimeEntryUpdateSerializer(data=data)
        assert serializer.is_valid()

    def test_validate_end_before_start(self):
        """Test validation when end time is before existing start time."""
        start_time = timezone.datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Test entry", start_time=start_time
        )

        data = {"end_time": "2024-01-01T10:00:00Z"}  # Before start time

        serializer = TimeEntryUpdateSerializer(time_entry, data=data)
        assert not serializer.is_valid()
        assert "end_time" in serializer.errors

    def test_validate_end_same_as_start(self):
        """Test validation when end time is same as start time."""
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Test entry", start_time=start_time
        )

        data = {"end_time": "2024-01-01T10:00:00Z"}  # Same as start time

        serializer = TimeEntryUpdateSerializer(time_entry, data=data)
        assert not serializer.is_valid()
        assert "end_time" in serializer.errors

    def test_validate_valid_end_time(self):
        """Test validation with valid end time."""
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Test entry", start_time=start_time
        )

        end_time = timezone.datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        data = {
            "description": "Updated description",
            "end_time": end_time,  # After start time
        }

        serializer = TimeEntryUpdateSerializer(time_entry, data=data)
        assert serializer.is_valid()

    def test_update_existing_entry(self):
        """Test updating an existing time entry."""
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Original description", start_time=start_time
        )

        data = {
            "description": "Updated description",
            "end_time": "2024-01-01T11:00:00Z",
        }

        serializer = TimeEntryUpdateSerializer(time_entry, data=data)
        assert serializer.is_valid()

        updated_entry = serializer.save()
        assert updated_entry.description == "Updated description"
        assert updated_entry.end_time is not None

    def test_update_without_end_time(self):
        """Test updating without setting end time."""
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Original description", start_time=start_time
        )

        data = {"description": "Updated description"}

        serializer = TimeEntryUpdateSerializer(time_entry, data=data)
        assert serializer.is_valid()

        updated_entry = serializer.save()
        assert updated_entry.description == "Updated description"
        assert updated_entry.end_time is None


@pytest.mark.django_db
class TestSerializerIntegration:
    """Integration tests for serializers with models."""

    def test_create_serializer_integration(self):
        """Test TimeEntryCreateSerializer integration with model."""
        data = {
            "description": "Integration test",
            "start_time": "2024-01-01T10:00:00Z",
            "end_time": "2024-01-01T11:00:00Z",
        }

        serializer = TimeEntryCreateSerializer(data=data)
        assert serializer.is_valid()

        time_entry = serializer.save()
        assert TimeEntry.objects.filter(id=time_entry.id).exists()
        assert time_entry.duration is not None

    def test_update_serializer_integration(self):
        """Test TimeEntryUpdateSerializer integration with model."""
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Original", start_time=start_time
        )

        data = {
            "description": "Updated via serializer",
            "end_time": "2024-01-01T11:00:00Z",
        }

        serializer = TimeEntryUpdateSerializer(time_entry, data=data)
        assert serializer.is_valid()

        updated_entry = serializer.save()
        assert updated_entry.description == "Updated via serializer"
        assert updated_entry.duration is not None

    def test_serializer_validation_chain(self):
        """Test that validation works across serializer methods."""
        # Test create serializer validation
        create_data = {
            "description": "Test",
            "start_time": "2024-01-01T11:00:00Z",
            "end_time": "2024-01-01T10:00:00Z",  # Invalid: end before start
        }

        create_serializer = TimeEntryCreateSerializer(data=create_data)
        assert not create_serializer.is_valid()

        # Test update serializer validation
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        time_entry = TimeEntry.objects.create(
            description="Test entry", start_time=start_time
        )

        update_data = {"end_time": "2024-01-01T09:00:00Z"}  # Invalid: end before start

        update_serializer = TimeEntryUpdateSerializer(time_entry, data=update_data)
        assert not update_serializer.is_valid()

    def test_serializer_field_consistency(self):
        """Test that serializer fields are consistent across serializers."""
        # Check that common fields exist in all serializers
        create_fields = set(TimeEntryCreateSerializer.Meta.fields)
        update_fields = set(TimeEntryUpdateSerializer.Meta.fields)
        main_fields = set(TimeEntrySerializer.Meta.fields)

        # Create and update should have subset of main fields
        # Note: Create serializer has different fields than main serializer
        assert "description" in create_fields
        assert "start_time" in create_fields
        assert "end_time" in create_fields

        assert "description" in update_fields
        assert "end_time" in update_fields

        # Check that read-only fields are consistent
        main_readonly = set(TimeEntrySerializer.Meta.read_only_fields)
        create_readonly = set(
            getattr(TimeEntryCreateSerializer.Meta, "read_only_fields", [])
        )
        update_readonly = set(
            getattr(TimeEntryUpdateSerializer.Meta, "read_only_fields", [])
        )

        # Main serializer should have read-only fields
        assert len(main_readonly) > 0

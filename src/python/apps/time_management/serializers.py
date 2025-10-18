from django.utils import timezone

from rest_framework import serializers

from .models import TimeEntry


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimeEntry model."""

    class Meta:
        model = TimeEntry
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "duration"]

    def validate_start_time(self, value):
        """Validate start time."""
        if value > timezone.now():
            raise serializers.ValidationError("Start time cannot be in the future")
        return value

    def validate(self, data):
        """Validate the entire data set."""
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")

        return data


class TimeEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating time entries."""

    class Meta:
        model = TimeEntry
        fields = ["description", "start_time", "end_time"]

    def validate_start_time(self, value):
        """Validate start time."""
        if value > timezone.now():
            raise serializers.ValidationError("Start time cannot be in the future")
        return value

    def validate(self, data):
        """Validate the entire data set."""
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")

        return data


class TimeEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating time entries."""

    class Meta:
        model = TimeEntry
        fields = ["description", "end_time"]

    def validate_end_time(self, value):
        """Validate end time."""
        if (
            self.instance
            and self.instance.start_time
            and value <= self.instance.start_time
        ):
            raise serializers.ValidationError("End time must be after start time")
        return value

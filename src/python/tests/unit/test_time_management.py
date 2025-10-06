from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.time_management.models import TimeEntry


class TimeAPITestCase(APITestCase):
    def test_current_time_endpoint(self):
        """Test the current time API endpoint."""
        url = reverse("current_time")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("current_time", response.data)
        self.assertIn("timezone", response.data)
        self.assertIn("unix_timestamp", response.data)

    def test_health_check_endpoint(self):
        """Test the health check API endpoint."""
        url = reverse("health_check")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")


class TimeEntryAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data."""
        # Clear any existing data
        TimeEntry.objects.all().delete()

        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(hours=2)

        self.time_entry = TimeEntry.objects.create(
            description="Test time entry",
            start_time=self.start_time,
            end_time=self.end_time,
        )

    def test_list_time_entries(self):
        """Test listing time entries."""
        url = reverse("timeentry-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that our test entry is in the results
        if isinstance(response.data, dict) and "results" in response.data:
            # Paginated response
            descriptions = [entry["description"] for entry in response.data["results"]]
        else:
            # Non-paginated response
            descriptions = [entry["description"] for entry in response.data]
        self.assertIn("Test time entry", descriptions)

    def test_create_time_entry(self):
        """Test creating a time entry."""
        url = reverse("timeentry-list")
        data = {
            "description": "New time entry",
            "start_time": timezone.now().isoformat(),
            "end_time": (timezone.now() + timezone.timedelta(hours=1)).isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimeEntry.objects.count(), 2)

    def test_get_time_entry_detail(self):
        """Test getting a specific time entry."""
        url = reverse("timeentry-detail", kwargs={"pk": self.time_entry.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], "Test time entry")

    def test_start_timer(self):
        """Test starting a new timer."""
        url = reverse("timeentry-start-timer")
        data = {
            "description": "New timer",
            "start_time": timezone.now().isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["start_time"])
        self.assertIsNone(response.data["end_time"])

    def test_stop_timer(self):
        """Test stopping a timer."""
        # Create a running timer
        running_timer = TimeEntry.objects.create(
            description="Running timer", start_time=timezone.now()
        )

        url = reverse("timeentry-stop-timer", kwargs={"pk": running_timer.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["end_time"])
        self.assertIsNotNone(response.data["duration"])

    def test_stop_already_stopped_timer(self):
        """Test stopping an already stopped timer."""
        url = reverse("timeentry-stop-timer", kwargs={"pk": self.time_entry.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_get_active_timers(self):
        """Test getting active timers."""
        # Create a running timer
        TimeEntry.objects.create(description="Running timer", start_time=timezone.now())

        url = reverse("timeentry-active-timers")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_statistics(self):
        """Test getting time entry statistics."""
        url = reverse("timeentry-statistics")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_entries", response.data)
        self.assertIn("total_duration", response.data)
        self.assertIn("total_seconds", response.data)
        self.assertEqual(response.data["total_entries"], 1)

    def test_validation_start_time_future(self):
        """Test validation for future start time."""
        url = reverse("timeentry-list")
        future_time = timezone.now() + timezone.timedelta(hours=1)
        data = {
            "description": "Future time entry",
            "start_time": future_time.isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_end_before_start(self):
        """Test validation for end time before start time."""
        url = reverse("timeentry-list")
        start_time = timezone.now()
        end_time = start_time - timezone.timedelta(hours=1)
        data = {
            "description": "Invalid time entry",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

"""
API Views Tests

Tests for the API view endpoints across all apps.
"""

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.time_management.models import TimeEntry


class TimeManagementAPITestCase(APITestCase):
    """Test cases for time management API views."""

    def setUp(self):
        """Set up test data."""
        TimeEntry.objects.all().delete()

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

    def test_time_entry_list(self):
        """Test listing time entries."""
        # Create test data
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end_time = timezone.datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        TimeEntry.objects.create(
            description="Test entry",
            start_time=start_time,
            end_time=end_time
        )

        url = reverse("timeentry-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_time_entry_create(self):
        """Test creating a time entry."""
        url = reverse("timeentry-list")
        data = {
            "description": "New test entry",
            "start_time": "2024-01-01T10:00:00Z",
            "end_time": "2024-01-01T11:00:00Z"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimeEntry.objects.count(), 1)

    def test_time_entry_statistics(self):
        """Test time entry statistics endpoint."""
        # Create test data
        start_time1 = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end_time1 = timezone.datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        start_time2 = timezone.datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end_time2 = timezone.datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
        
        TimeEntry.objects.create(
            description="Test entry 1",
            start_time=start_time1,
            end_time=end_time1
        )
        TimeEntry.objects.create(
            description="Test entry 2",
            start_time=start_time2,
            end_time=end_time2
        )

        url = reverse("timeentry-statistics")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_entries"], 2)
        self.assertIn("total_duration", response.data)
        self.assertIn("total_seconds", response.data)

    def test_start_timer(self):
        """Test starting a timer."""
        url = reverse("timeentry-start-timer")
        data = {
            "description": "Timer test",
            "start_time": "2024-01-01T10:00:00Z"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TimeEntry.objects.count(), 1)

    def test_active_timers(self):
        """Test getting active timers."""
        # Create an active timer (no end_time)
        start_time = timezone.datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        TimeEntry.objects.create(
            description="Active timer",
            start_time=start_time
        )

        url = reverse("timeentry-active-timers")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)


class RenogyDevicesAPITestCase(APITestCase):
    """Test cases for Renogy devices API views."""

    def test_renogy_device_list(self):
        """Test listing Renogy devices."""
        url = reverse("renogy_device_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("devices", response.data)
        self.assertIn("total_count", response.data)

    def test_renogy_device_add(self):
        """Test adding a Renogy device."""
        url = reverse("renogy_device_add")
        data = {
            "device_address": "F8:55:48:17:99:EB",
            "timeout": 10
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("device_address", response.data)

    def test_renogy_device_add_invalid_address(self):
        """Test adding a Renogy device with invalid address."""
        url = reverse("renogy_device_add")
        data = {
            "device_address": "invalid-address",
            "timeout": 10
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_renogy_device_status(self):
        """Test getting Renogy device status."""
        # First add a device
        add_url = reverse("renogy_device_add")
        add_data = {"device_address": "F8:55:48:17:99:EB"}
        self.client.post(add_url, add_data, format='json')

        # Then get its status
        status_url = reverse("renogy_device_status", kwargs={"device_address": "F8:55:48:17:99:EB"})
        response = self.client.get(status_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("device_address", response.data)
        self.assertIn("connected", response.data)

    def test_renogy_device_not_found(self):
        """Test getting status of non-existent device."""
        url = reverse("renogy_device_status", kwargs={"device_address": "00:00:00:00:00:00"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_renogy_connect_all(self):
        """Test connecting to all Renogy devices."""
        url = reverse("renogy_connect_all")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("results", response.data)

    def test_renogy_all_data(self):
        """Test getting data from all Renogy devices."""
        url = reverse("renogy_all_data")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("devices", response.data)
        self.assertIn("total_devices", response.data)


class DS18B20SensorsAPITestCase(APITestCase):
    """Test cases for DS18B20 sensors API views."""

    def test_ds18b20_sensor_list(self):
        """Test listing DS18B20 sensors."""
        url = reverse("ds18b20_sensor_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sensors", response.data)
        self.assertIn("total_count", response.data)

    def test_ds18b20_sensor_add(self):
        """Test adding a DS18B20 sensor."""
        url = reverse("ds18b20_sensor_add")
        data = {
            "sensor_id": "28-0123456789ab",
            "sensor_name": "Test Sensor"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("sensor_id", response.data)

    def test_ds18b20_sensor_add_missing_data(self):
        """Test adding a DS18B20 sensor with missing data."""
        url = reverse("ds18b20_sensor_add")
        data = {"sensor_id": "28-0123456789ab"}  # Missing sensor_name

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ds18b20_sensor_info(self):
        """Test getting DS18B20 sensor info."""
        # First add a sensor
        add_url = reverse("ds18b20_sensor_add")
        add_data = {
            "sensor_id": "28-0123456789ab",
            "sensor_name": "Test Sensor"
        }
        self.client.post(add_url, add_data, format='json')

        # Then get its info
        info_url = reverse("ds18b20_sensor_info", kwargs={"sensor_id": "28-0123456789ab"})
        response = self.client.get(info_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sensor_id", response.data)
        self.assertIn("sensor_name", response.data)

    def test_ds18b20_sensor_not_found(self):
        """Test getting info of non-existent sensor."""
        url = reverse("ds18b20_sensor_info", kwargs={"sensor_id": "28-000000000000"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ds18b20_discover_sensors(self):
        """Test discovering DS18B20 sensors."""
        url = reverse("ds18b20_discover_sensors")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sensor_ids", response.data)
        self.assertIn("count", response.data)

    def test_ds18b20_sensor_summary(self):
        """Test getting DS18B20 sensor summary."""
        url = reverse("ds18b20_sensor_summary")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_sensors", response.data)
        self.assertIn("available_sensors", response.data)
        self.assertIn("sensors", response.data)

    def test_ds18b20_all_temperatures(self):
        """Test getting temperatures from all DS18B20 sensors."""
        url = reverse("ds18b20_all_temperatures")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("readings", response.data)
        self.assertIn("total_sensors", response.data)
        self.assertIn("valid_readings", response.data)


class DocumentationAPITestCase(APITestCase):
    """Test cases for documentation API views."""

    def test_api_info(self):
        """Test API info endpoint."""
        url = reverse("api_info")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data)
        self.assertIn("version", response.data)
        self.assertIn("endpoints", response.data)

    def test_api_examples(self):
        """Test API examples endpoint."""
        url = reverse("api_examples")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("examples", response.data)

    def test_api_status(self):
        """Test API status endpoint."""
        url = reverse("api_status")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertIn("components", response.data)

    def test_api_changelog(self):
        """Test API changelog endpoint."""
        url = reverse("api_changelog")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("versions", response.data)

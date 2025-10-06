"""
Test module for DS18B20 temperature sensor functionality.

This module contains test cases for the DS18B20Sensor class and related functionality.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from apps.ds18b20_sensors.sensor import (
    DS18B20Sensor,
    DS18B20SensorManager,
    TemperatureReading,
    discover_all_ds18b20_sensors,
)


class TestDS18B20Sensor:
    """Test class for DS18B20Sensor."""

    TEST_SENSOR_ID = "28-0123456789ab"
    TEST_SENSOR_NAME = "Test Temperature Sensor"

    def setup_method(self):
        """Set up test fixtures."""
        self.sensor = DS18B20Sensor(self.TEST_SENSOR_ID, self.TEST_SENSOR_NAME)

    def test_sensor_initialization(self):
        """Test sensor initialization with correct parameters."""
        assert self.sensor.sensor_id == self.TEST_SENSOR_ID
        assert self.sensor.sensor_name == self.TEST_SENSOR_NAME
        assert self.sensor.base_dir == Path("/sys/bus/w1/devices/")
        assert self.sensor.device_path == Path(
            f"/sys/bus/w1/devices/{self.TEST_SENSOR_ID}"
        )
        assert self.sensor.device_file == Path(
            f"/sys/bus/w1/devices/{self.TEST_SENSOR_ID}/w1_slave"
        )

    def test_sensor_initialization_with_custom_base_dir(self):
        """Test sensor initialization with custom base directory."""
        custom_base_dir = "/custom/w1/devices/"
        sensor = DS18B20Sensor(
            self.TEST_SENSOR_ID, self.TEST_SENSOR_NAME, custom_base_dir
        )
        assert sensor.base_dir == Path(custom_base_dir)
        assert sensor.device_path == Path(f"{custom_base_dir}{self.TEST_SENSOR_ID}")

    @patch("os.system")
    def test_initialize_1wire_interface(self, mock_system):
        """Test 1-Wire interface initialization."""
        self.sensor._initialize_1wire_interface()
        mock_system.assert_any_call("modprobe w1-gpio")
        mock_system.assert_any_call("modprobe w1-therm")

    @patch("builtins.open", new_callable=mock_open, read_data="YES\n t=25500")
    @patch("pathlib.Path.exists")
    def test_read_raw_data_success(self, mock_exists, mock_file):
        """Test successful raw data reading."""
        mock_exists.return_value = True
        lines = self.sensor._read_raw_data()
        assert lines == ["YES\n", " t=25500"]
        mock_file.assert_called_once()

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_read_raw_data_file_not_found(self, mock_file):
        """Test raw data reading when file not found."""
        lines = self.sensor._read_raw_data()
        assert lines is None

    def test_parse_temperature_valid_data(self):
        """Test temperature parsing with valid data."""
        lines = ["YES\n", " t=25500"]
        temp = self.sensor._parse_temperature(lines)
        assert temp == 25.5

    def test_parse_temperature_invalid_data(self):
        """Test temperature parsing with invalid data."""
        lines = ["NO\n", " t=25500"]
        temp = self.sensor._parse_temperature(lines)
        assert temp is None

    def test_parse_temperature_missing_temperature(self):
        """Test temperature parsing when temperature value is missing."""
        lines = ["YES\n", " no temperature"]
        temp = self.sensor._parse_temperature(lines)
        assert temp is None

    def test_parse_temperature_invalid_format(self):
        """Test temperature parsing with invalid format."""
        lines = ["YES\n", " invalid"]
        temp = self.sensor._parse_temperature(lines)
        assert temp is None

    @patch.object(DS18B20Sensor, "_read_raw_data")
    @patch.object(DS18B20Sensor, "_parse_temperature")
    @patch("pathlib.Path.exists")
    def test_read_temperature_success(self, mock_exists, mock_parse, mock_read):
        """Test successful temperature reading."""
        mock_exists.return_value = True
        mock_read.return_value = ["YES\n", " t=25500"]
        mock_parse.return_value = 25.5

        reading = self.sensor.read_temperature()

        assert reading.sensor_id == self.TEST_SENSOR_ID
        assert reading.sensor_name == self.TEST_SENSOR_NAME
        assert reading.temperature_celsius == 25.5
        assert reading.temperature_fahrenheit == 77.9
        assert reading.is_valid is True
        assert reading.error_message is None
        assert isinstance(reading.timestamp, datetime)

    @patch("pathlib.Path.exists")
    def test_read_temperature_sensor_not_found(self, mock_exists):
        """Test temperature reading when sensor not found."""
        mock_exists.return_value = False
        reading = self.sensor.read_temperature()

        assert reading.is_valid is False
        assert "not found" in reading.error_message

    @patch.object(DS18B20Sensor, "_read_raw_data")
    @patch("pathlib.Path.exists")
    def test_read_temperature_read_failure(self, mock_exists, mock_read):
        """Test temperature reading when read fails."""
        mock_exists.return_value = True
        mock_read.return_value = None

        reading = self.sensor.read_temperature()

        assert reading.is_valid is False
        assert "Failed to read sensor data" in reading.error_message

    @patch.object(DS18B20Sensor, "_read_raw_data")
    @patch.object(DS18B20Sensor, "_parse_temperature")
    @patch("pathlib.Path.exists")
    def test_read_temperature_parse_failure(self, mock_exists, mock_parse, mock_read):
        """Test temperature reading when parsing fails."""
        mock_exists.return_value = True
        mock_read.return_value = ["YES\n", " t=25500"]
        mock_parse.return_value = None

        reading = self.sensor.read_temperature()

        assert reading.is_valid is False
        assert "Failed to read valid temperature" in reading.error_message

    @patch("pathlib.Path.exists")
    def test_is_available_true(self, mock_exists):
        """Test sensor availability when device exists."""
        mock_exists.return_value = True
        assert self.sensor.is_available() is True

    @patch("pathlib.Path.exists")
    def test_is_available_false(self, mock_exists):
        """Test sensor availability when device doesn't exist."""
        mock_exists.return_value = False
        assert self.sensor.is_available() is False

    def test_get_sensor_info(self):
        """Test sensor information retrieval."""
        info = self.sensor.get_sensor_info()

        assert info["sensor_id"] == self.TEST_SENSOR_ID
        assert info["sensor_name"] == self.TEST_SENSOR_NAME
        assert "device_path" in info
        assert "device_file" in info
        assert "is_available" in info
        assert "base_dir" in info

    def test_sensor_string_representation(self):
        """Test string representation of sensor."""
        with patch.object(self.sensor, "is_available", return_value=True):
            sensor_str = str(self.sensor)
            assert self.TEST_SENSOR_ID in sensor_str
            assert self.TEST_SENSOR_NAME in sensor_str
            assert "available" in sensor_str

    def test_sensor_repr(self):
        """Test detailed string representation."""
        sensor_repr = repr(self.sensor)
        assert self.TEST_SENSOR_ID in sensor_repr
        assert self.TEST_SENSOR_NAME in sensor_repr
        assert "DS18B20Sensor" in sensor_repr


class TestDS18B20SensorManager:
    """Test class for DS18B20SensorManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = DS18B20SensorManager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        assert isinstance(self.manager.sensors, dict)
        assert len(self.manager.sensors) == 0
        assert self.manager.base_dir == Path("/sys/bus/w1/devices/")

    @patch("glob.glob")
    def test_discover_sensors(self, mock_glob):
        """Test sensor discovery."""
        mock_glob.return_value = [
            "/sys/bus/w1/devices/28-0123456789ab",
            "/sys/bus/w1/devices/28-0123456789cd",
        ]

        sensor_ids = self.manager.discover_sensors()

        assert sensor_ids == ["28-0123456789ab", "28-0123456789cd"]
        mock_glob.assert_called_once_with(str(Path("/sys/bus/w1/devices/28*")))

    def test_add_sensor(self):
        """Test adding a sensor to the manager."""
        sensor_id = "28-0123456789ab"
        sensor_name = "Test Sensor"

        sensor = self.manager.add_sensor(sensor_id, sensor_name)

        assert isinstance(sensor, DS18B20Sensor)
        assert sensor.sensor_id == sensor_id
        assert sensor.sensor_name == sensor_name
        assert sensor_id in self.manager.sensors

    def test_remove_sensor(self):
        """Test removing a sensor from the manager."""
        sensor_id = "28-0123456789ab"
        self.manager.add_sensor(sensor_id, "Test Sensor")

        result = self.manager.remove_sensor(sensor_id)

        assert result is True
        assert sensor_id not in self.manager.sensors

    def test_remove_nonexistent_sensor(self):
        """Test removing a non-existent sensor."""
        result = self.manager.remove_sensor("nonexistent")
        assert result is False

    def test_get_sensor(self):
        """Test getting a sensor from the manager."""
        sensor_id = "28-0123456789ab"
        added_sensor = self.manager.add_sensor(sensor_id, "Test Sensor")

        retrieved_sensor = self.manager.get_sensor(sensor_id)

        assert retrieved_sensor is added_sensor

    def test_get_nonexistent_sensor(self):
        """Test getting a non-existent sensor."""
        sensor = self.manager.get_sensor("nonexistent")
        assert sensor is None

    def test_list_sensors(self):
        """Test listing all sensors."""
        self.manager.add_sensor("28-0123456789ab", "Sensor 1")
        self.manager.add_sensor("28-0123456789cd", "Sensor 2")

        sensors = self.manager.list_sensors()

        assert len(sensors) == 2
        sensor_ids = [sensor["sensor_id"] for sensor in sensors]
        assert "28-0123456789ab" in sensor_ids
        assert "28-0123456789cd" in sensor_ids

    @patch.object(DS18B20Sensor, "read_temperature")
    def test_read_all_temperatures(self, mock_read):
        """Test reading temperatures from all sensors."""
        # Mock temperature reading
        mock_reading = TemperatureReading(
            sensor_id="28-0123456789ab",
            sensor_name="Test Sensor",
            temperature_celsius=25.5,
            temperature_fahrenheit=77.9,
            timestamp=datetime.now(),
        )
        mock_read.return_value = mock_reading

        self.manager.add_sensor("28-0123456789ab", "Test Sensor")

        readings = self.manager.read_all_temperatures()

        assert len(readings) == 1
        assert readings[0].sensor_id == "28-0123456789ab"
        assert readings[0].temperature_celsius == 25.5

    def test_get_sensor_summary(self):
        """Test getting sensor summary."""
        self.manager.add_sensor("28-0123456789ab", "Sensor 1")
        self.manager.add_sensor("28-0123456789cd", "Sensor 2")

        summary = self.manager.get_sensor_summary()

        assert summary["total_sensors"] == 2
        assert "available_sensors" in summary
        assert "unavailable_sensors" in summary
        assert len(summary["sensors"]) == 2


class TestTemperatureReading:
    """Test class for TemperatureReading data structure."""

    def test_temperature_reading_initialization(self):
        """Test temperature reading initialization."""
        reading = TemperatureReading(
            sensor_id="28-0123456789ab",
            sensor_name="Test Sensor",
            temperature_celsius=25.5,
            temperature_fahrenheit=77.9,
            timestamp=datetime.now(),
        )

        assert reading.sensor_id == "28-0123456789ab"
        assert reading.sensor_name == "Test Sensor"
        assert reading.temperature_celsius == 25.5
        assert reading.temperature_fahrenheit == 77.9
        assert reading.is_valid is True
        assert reading.error_message is None

    def test_temperature_reading_to_dict(self):
        """Test temperature reading to dictionary conversion."""
        timestamp = datetime.now()
        reading = TemperatureReading(
            sensor_id="28-0123456789ab",
            sensor_name="Test Sensor",
            temperature_celsius=25.5,
            temperature_fahrenheit=77.9,
            timestamp=timestamp,
        )

        data = reading.to_dict()

        assert data["sensor_id"] == "28-0123456789ab"
        assert data["sensor_name"] == "Test Sensor"
        assert data["temperature_celsius"] == 25.5
        assert data["temperature_fahrenheit"] == 77.9
        assert data["timestamp"] == timestamp.isoformat()
        assert data["is_valid"] is True
        assert data["error_message"] is None

    def test_temperature_reading_with_error(self):
        """Test temperature reading with error."""
        reading = TemperatureReading(
            sensor_id="28-0123456789ab",
            sensor_name="Test Sensor",
            temperature_celsius=0.0,
            temperature_fahrenheit=32.0,
            timestamp=datetime.now(),
            error_message="Sensor not found",
            is_valid=False,
        )

        assert reading.is_valid is False
        assert reading.error_message == "Sensor not found"


class TestUtilityFunctions:
    """Test class for utility functions."""

    @patch("apps.ds18b20_sensors.sensor.DS18B20SensorManager")
    def test_discover_all_ds18b20_sensors(self, mock_manager_class):
        """Test discover_all_ds18b20_sensors utility function."""
        mock_manager = Mock()
        mock_manager.discover_sensors.return_value = [
            "28-0123456789ab",
            "28-0123456789cd",
        ]
        mock_manager_class.return_value = mock_manager

        sensor_ids = discover_all_ds18b20_sensors()

        assert sensor_ids == ["28-0123456789ab", "28-0123456789cd"]
        mock_manager_class.assert_called_once_with("/sys/bus/w1/devices/")

    def test_create_sensor_from_id(self):
        """Test create_sensor_from_id utility function."""
        from apps.ds18b20_sensors.sensor import create_sensor_from_id

        sensor = create_sensor_from_id("28-0123456789ab")

        assert sensor.sensor_id == "28-0123456789ab"
        assert sensor.sensor_name == "Sensor 28-0123456789ab"

    def test_create_sensor_from_id_with_name(self):
        """Test create_sensor_from_id with custom name."""
        from apps.ds18b20_sensors.sensor import create_sensor_from_id

        sensor = create_sensor_from_id("28-0123456789ab", "Custom Name")

        assert sensor.sensor_id == "28-0123456789ab"
        assert sensor.sensor_name == "Custom Name"


# Pytest fixtures for common test data
@pytest.fixture
def test_sensor_id():
    """Fixture providing a test sensor ID."""
    return "28-0123456789ab"


@pytest.fixture
def test_sensor_name():
    """Fixture providing a test sensor name."""
    return "Test Temperature Sensor"


@pytest.fixture
def ds18b20_sensor(test_sensor_id, test_sensor_name):
    """Fixture providing a DS18B20Sensor instance."""
    return DS18B20Sensor(test_sensor_id, test_sensor_name)


@pytest.fixture
def ds18b20_manager():
    """Fixture providing a DS18B20SensorManager instance."""
    return DS18B20SensorManager()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])

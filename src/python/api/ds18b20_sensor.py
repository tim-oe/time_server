"""
DS18B20 Temperature Sensor Module

This module provides functionality to read temperature from DS18B20 sensors
connected via the 1-Wire interface on Raspberry Pi and other Linux systems.
"""

import glob
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TemperatureReading:
    """Data structure for temperature sensor readings."""

    sensor_id: str
    sensor_name: str
    temperature_celsius: float
    temperature_fahrenheit: float
    timestamp: datetime
    error_message: Optional[str] = None
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "sensor_id": self.sensor_id,
            "sensor_name": self.sensor_name,
            "temperature_celsius": round(self.temperature_celsius, 2),
            "temperature_fahrenheit": round(self.temperature_fahrenheit, 2),
            "timestamp": self.timestamp.isoformat(),
            "error_message": self.error_message,
            "is_valid": self.is_valid,
        }


class DS18B20Sensor:
    """
    DS18B20 Temperature Sensor handler.

    This class manages reading temperature from DS18B20 sensors
    connected via the 1-Wire interface.
    """

    def __init__(
        self, sensor_id: str, sensor_name: str, base_dir: str = "/sys/bus/w1/devices/"
    ):
        """
        Initialize DS18B20 sensor handler.

        Args:
            sensor_id: The unique sensor ID (e.g., "28-0123456789ab")
            sensor_name: User-friendly name for the sensor (e.g., "Battery Temperature")
            base_dir: Base directory for 1-Wire devices (default: /sys/bus/w1/devices/)
        """
        self.sensor_id = sensor_id
        self.sensor_name = sensor_name
        self.base_dir = Path(base_dir)
        self.device_path = self.base_dir / sensor_id
        self.device_file = self.device_path / "w1_slave"

        # Initialize 1-Wire interface if not already done
        self._initialize_1wire_interface()

        # Verify sensor exists
        if not self.device_path.exists():
            logger.warning(f"Sensor {sensor_id} not found at {self.device_path}")

    def _initialize_1wire_interface(self):
        """Initialize the 1-Wire interface modules."""
        try:
            # Load required kernel modules
            os.system("modprobe w1-gpio")
            os.system("modprobe w1-therm")
            logger.debug("1-Wire interface modules loaded")
        except Exception as e:
            logger.error(f"Failed to initialize 1-Wire interface: {e}")

    def _read_raw_data(self) -> Optional[List[str]]:
        """
        Read raw data from the sensor device file.

        Returns:
            List of lines from the device file, or None if error
        """
        try:
            if not self.device_file.exists():
                logger.error(f"Device file not found: {self.device_file}")
                return None

            with open(self.device_file, "r") as f:
                lines = f.readlines()
            return lines
        except Exception as e:
            logger.error(f"Error reading from device file {self.device_file}: {e}")
            return None

    def _parse_temperature(self, lines: List[str]) -> Optional[float]:
        """
        Parse temperature from raw sensor data.

        Args:
            lines: Raw lines from the sensor device file

        Returns:
            Temperature in Celsius, or None if parsing failed
        """
        try:
            # Check if the reading is valid (ends with 'YES')
            if not lines or len(lines) < 2:
                return None

            if lines[0].strip()[-3:] != "YES":
                logger.warning(f"Invalid reading from sensor {self.sensor_id}")
                return None

            # Extract temperature value
            equals_pos = lines[1].find("t=")
            if equals_pos == -1:
                logger.warning(
                    f"Temperature value not found in sensor {self.sensor_id}"
                )
                return None

            temp_string = lines[1][equals_pos + 2 :]
            temp_celsius = float(temp_string) / 1000.0

            return temp_celsius
        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing temperature from sensor {self.sensor_id}: {e}")
            return None

    def read_temperature(
        self, max_retries: int = 3, retry_delay: float = 0.2
    ) -> TemperatureReading:
        """
        Read temperature from the sensor.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            TemperatureReading object with sensor data
        """
        reading = TemperatureReading(
            sensor_id=self.sensor_id,
            sensor_name=self.sensor_name,
            temperature_celsius=0.0,
            temperature_fahrenheit=0.0,
            timestamp=datetime.now(),
        )

        # Check if sensor exists
        if not self.device_path.exists():
            reading.error_message = f"Sensor {self.sensor_id} not found"
            reading.is_valid = False
            return reading

        # Attempt to read temperature with retries
        for attempt in range(max_retries):
            lines = self._read_raw_data()
            if lines is None:
                if attempt == max_retries - 1:
                    reading.error_message = "Failed to read sensor data"
                    reading.is_valid = False
                    return reading
                time.sleep(retry_delay)
                continue

            temp_celsius = self._parse_temperature(lines)
            if temp_celsius is not None:
                # Successfully read temperature
                reading.temperature_celsius = temp_celsius
                reading.temperature_fahrenheit = temp_celsius * 9.0 / 5.0 + 32.0
                reading.is_valid = True
                logger.debug(
                    f"Successfully read temperature from {self.sensor_name}: {temp_celsius:.2f}°C"
                )
                return reading

            # Wait before retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        # All retries failed
        reading.error_message = (
            f"Failed to read valid temperature after {max_retries} attempts"
        )
        reading.is_valid = False
        return reading

    def is_available(self) -> bool:
        """
        Check if the sensor is available and accessible.

        Returns:
            True if sensor is available, False otherwise
        """
        return self.device_path.exists() and self.device_file.exists()

    def get_sensor_info(self) -> Dict[str, Any]:
        """
        Get information about the sensor.

        Returns:
            Dictionary with sensor information
        """
        return {
            "sensor_id": self.sensor_id,
            "sensor_name": self.sensor_name,
            "device_path": str(self.device_path),
            "device_file": str(self.device_file),
            "is_available": self.is_available(),
            "base_dir": str(self.base_dir),
        }

    def __str__(self) -> str:
        """String representation of the sensor."""
        status = "available" if self.is_available() else "unavailable"
        return f"DS18B20Sensor(id={self.sensor_id}, name='{self.sensor_name}', status={status})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"DS18B20Sensor(sensor_id='{self.sensor_id}', "
            f"sensor_name='{self.sensor_name}', "
            f"base_dir='{self.base_dir}')"
        )


class DS18B20SensorManager:
    """
    Manager class for handling multiple DS18B20 sensors.
    """

    def __init__(self, base_dir: str = "/sys/bus/w1/devices/"):
        """
        Initialize sensor manager.

        Args:
            base_dir: Base directory for 1-Wire devices
        """
        self.base_dir = Path(base_dir)
        self.sensors: Dict[str, DS18B20Sensor] = {}

        # Initialize 1-Wire interface
        self._initialize_1wire_interface()

    def _initialize_1wire_interface(self):
        """Initialize the 1-Wire interface modules."""
        try:
            os.system("modprobe w1-gpio")
            os.system("modprobe w1-therm")
            logger.debug("1-Wire interface modules loaded")
        except Exception as e:
            logger.error(f"Failed to initialize 1-Wire interface: {e}")

    def discover_sensors(self) -> List[str]:
        """
        Discover all available DS18B20 sensors.

        Returns:
            List of sensor IDs found
        """
        try:
            # Look for devices with ID starting with '28' (DS18B20 family)
            device_pattern = str(self.base_dir / "28*")
            device_folders = glob.glob(device_pattern)

            sensor_ids = []
            for folder in device_folders:
                sensor_id = Path(folder).name
                sensor_ids.append(sensor_id)

            logger.info(f"Discovered {len(sensor_ids)} DS18B20 sensors: {sensor_ids}")
            return sensor_ids
        except Exception as e:
            logger.error(f"Error discovering sensors: {e}")
            return []

    def add_sensor(self, sensor_id: str, sensor_name: str) -> DS18B20Sensor:
        """
        Add a sensor to the manager.

        Args:
            sensor_id: The unique sensor ID
            sensor_name: User-friendly name for the sensor

        Returns:
            The created sensor instance
        """
        sensor = DS18B20Sensor(sensor_id, sensor_name, str(self.base_dir))
        self.sensors[sensor_id] = sensor
        logger.info(f"Added sensor {sensor_id} with name '{sensor_name}'")
        return sensor

    def remove_sensor(self, sensor_id: str) -> bool:
        """
        Remove a sensor from the manager.

        Args:
            sensor_id: The sensor ID to remove

        Returns:
            True if sensor was removed, False if not found
        """
        if sensor_id in self.sensors:
            del self.sensors[sensor_id]
            logger.info(f"Removed sensor {sensor_id}")
            return True
        return False

    def get_sensor(self, sensor_id: str) -> Optional[DS18B20Sensor]:
        """
        Get a sensor by its ID.

        Args:
            sensor_id: The sensor ID

        Returns:
            Sensor instance or None if not found
        """
        return self.sensors.get(sensor_id)

    def list_sensors(self) -> List[Dict[str, Any]]:
        """
        List all managed sensors with their information.

        Returns:
            List of sensor information dictionaries
        """
        return [sensor.get_sensor_info() for sensor in self.sensors.values()]

    def read_all_temperatures(self) -> List[TemperatureReading]:
        """
        Read temperature from all managed sensors.

        Returns:
            List of temperature readings
        """
        readings = []
        for sensor in self.sensors.values():
            reading = sensor.read_temperature()
            readings.append(reading)
        return readings

    def read_available_temperatures(self) -> List[TemperatureReading]:
        """
        Read temperature from all available sensors only.

        Returns:
            List of temperature readings from available sensors
        """
        readings = []
        for sensor in self.sensors.values():
            if sensor.is_available():
                reading = sensor.read_temperature()
                readings.append(reading)
        return readings

    def get_sensor_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all sensors and their status.

        Returns:
            Dictionary with sensor summary information
        """
        total_sensors = len(self.sensors)
        available_sensors = sum(
            1 for sensor in self.sensors.values() if sensor.is_available()
        )

        return {
            "total_sensors": total_sensors,
            "available_sensors": available_sensors,
            "unavailable_sensors": total_sensors - available_sensors,
            "sensors": self.list_sensors(),
        }


# Utility functions
def discover_all_ds18b20_sensors(base_dir: str = "/sys/bus/w1/devices/") -> List[str]:
    """
    Discover all DS18B20 sensors on the system.

    Args:
        base_dir: Base directory for 1-Wire devices

    Returns:
        List of sensor IDs
    """
    manager = DS18B20SensorManager(base_dir)
    return manager.discover_sensors()


def create_sensor_from_id(sensor_id: str, sensor_name: str = None) -> DS18B20Sensor:
    """
    Create a sensor instance from sensor ID.

    Args:
        sensor_id: The sensor ID
        sensor_name: Optional user-friendly name (defaults to sensor_id)

    Returns:
        DS18B20Sensor instance
    """
    if sensor_name is None:
        sensor_name = f"Sensor {sensor_id}"

    return DS18B20Sensor(sensor_id, sensor_name)


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create sensor manager
    manager = DS18B20SensorManager()

    # Discover available sensors
    sensor_ids = manager.discover_sensors()

    if not sensor_ids:
        print(
            "No DS18B20 sensors found. Make sure sensors are connected and 1-Wire is enabled."
        )
        exit(1)

    # Add discovered sensors with friendly names
    for i, sensor_id in enumerate(sensor_ids):
        sensor_name = f"Temperature Sensor {i + 1}"
        manager.add_sensor(sensor_id, sensor_name)

    # Read temperatures from all sensors
    print("\nReading temperatures from all sensors...")
    readings = manager.read_all_temperatures()

    for reading in readings:
        if reading.is_valid:
            print(
                f"{reading.sensor_name} ({reading.sensor_id}): "
                f"{reading.temperature_celsius:.2f}°C / {reading.temperature_fahrenheit:.2f}°F"
            )
        else:
            print(
                f"{reading.sensor_name} ({reading.sensor_id}): ERROR - {reading.error_message}"
            )

    # Print sensor summary
    print("\nSensor Summary:")
    summary = manager.get_sensor_summary()
    print(f"Total sensors: {summary['total_sensors']}")
    print(f"Available sensors: {summary['available_sensors']}")
    print(f"Unavailable sensors: {summary['unavailable_sensors']}")

"""
Renogy Device Module

This module provides functionality to communicate with Renogy devices via Bluetooth.
It handles device connection, data reading, and error handling.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from renogy_modbus import RenogyModbus

    RENOGY_AVAILABLE = True
except ImportError:
    RENOGY_AVAILABLE = False
    RenogyModbus = None

logger = logging.getLogger(__name__)


@dataclass
class RenogyDeviceData:
    """Data structure for Renogy device information."""

    device_address: str
    battery_voltage: Optional[float] = None
    battery_current: Optional[float] = None
    battery_power: Optional[float] = None
    battery_soc: Optional[int] = None  # State of Charge percentage
    battery_temperature: Optional[float] = None
    pv_voltage: Optional[float] = None  # Photovoltaic voltage
    pv_current: Optional[float] = None
    pv_power: Optional[float] = None
    load_voltage: Optional[float] = None
    load_current: Optional[float] = None
    load_power: Optional[float] = None
    timestamp: Optional[datetime] = None
    connection_status: str = "disconnected"
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "device_address": self.device_address,
            "battery_voltage": self.battery_voltage,
            "battery_current": self.battery_current,
            "battery_power": self.battery_power,
            "battery_soc": self.battery_soc,
            "battery_temperature": self.battery_temperature,
            "pv_voltage": self.pv_voltage,
            "pv_current": self.pv_current,
            "pv_power": self.pv_power,
            "load_voltage": self.load_voltage,
            "load_current": self.load_current,
            "load_power": self.load_power,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "connection_status": self.connection_status,
            "error_message": self.error_message,
        }


class RenogyDevice:
    """
    Renogy Device handler for Bluetooth communication.

    This class manages connection to a Renogy device via Bluetooth and
    provides methods to read device data.
    """

    def __init__(self, device_address: str, timeout: int = 10):
        """
        Initialize Renogy device handler.

        Args:
            device_address: Bluetooth MAC address of the device
                (e.g., "F8:55:48:17:99:EB")
            timeout: Connection timeout in seconds
        """
        self.device_address = device_address.upper()
        self.timeout = timeout
        self.connection = None
        self.is_connected = False

        if not RENOGY_AVAILABLE:
            logger.warning("renogy_modbus library not available. Using mock data.")

    async def connect(self) -> bool:
        """
        Connect to the Renogy device via Bluetooth.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not RENOGY_AVAILABLE:
                logger.info(f"Mock connection to device {self.device_address}")
                self.is_connected = True
                return True

            # Initialize the Renogy Modbus connection
            self.connection = RenogyModbus(
                device=self.device_address, baudrate=9600, timeout=self.timeout
            )

            # Test connection by reading basic data
            await self._test_connection()
            self.is_connected = True
            logger.info(
                f"Successfully connected to Renogy device {self.device_address}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to connect to device {self.device_address}: {str(e)}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Disconnect from the Renogy device."""
        try:
            if self.connection:
                # Close the connection if available
                if hasattr(self.connection, "close"):
                    self.connection.close()
                self.connection = None

            self.is_connected = False
            logger.info(f"Disconnected from device {self.device_address}")

        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    async def read_data(self) -> RenogyDeviceData:
        """
        Read all available data from the Renogy device.

        Returns:
            RenogyDeviceData: Device data object
        """
        data = RenogyDeviceData(device_address=self.device_address)
        data.timestamp = datetime.now()

        if not self.is_connected:
            data.connection_status = "disconnected"
            data.error_message = "Device not connected"
            return data

        try:
            if not RENOGY_AVAILABLE:
                # Return mock data for testing
                return self._get_mock_data()

            # Read battery data
            battery_data = await self._read_battery_data()
            if battery_data:
                data.battery_voltage = battery_data.get("voltage")
                data.battery_current = battery_data.get("current")
                data.battery_power = battery_data.get("power")
                data.battery_soc = battery_data.get("soc")
                data.battery_temperature = battery_data.get("temperature")

            # Read PV (solar panel) data
            pv_data = await self._read_pv_data()
            if pv_data:
                data.pv_voltage = pv_data.get("voltage")
                data.pv_current = pv_data.get("current")
                data.pv_power = pv_data.get("power")

            # Read load data
            load_data = await self._read_load_data()
            if load_data:
                data.load_voltage = load_data.get("voltage")
                data.load_current = load_data.get("current")
                data.load_power = load_data.get("power")

            data.connection_status = "connected"
            logger.debug(f"Successfully read data from device {self.device_address}")

        except Exception as e:
            data.connection_status = "error"
            data.error_message = str(e)
            logger.error(
                f"Error reading data from device {self.device_address}: {str(e)}"
            )

        return data

    async def _test_connection(self):
        """Test the connection by reading a basic register."""
        if not self.connection:
            raise Exception("No connection established")

        # Try to read a basic register to test connection
        # This is a placeholder - actual implementation depends on the library
        pass

    async def _read_battery_data(self) -> Optional[Dict[str, Any]]:
        """Read battery-related data from the device."""
        try:
            if not self.connection:
                return None

            # Placeholder for actual battery data reading
            # This would use the specific methods from renogy_modbus library
            return {
                "voltage": 12.5,  # V
                "current": 2.3,  # A
                "power": 28.75,  # W
                "soc": 85,  # %
                "temperature": 25.5,  # °C
            }

        except Exception as e:
            logger.error(f"Error reading battery data: {str(e)}")
            return None

    async def _read_pv_data(self) -> Optional[Dict[str, Any]]:
        """Read PV (solar panel) data from the device."""
        try:
            if not self.connection:
                return None

            # Placeholder for actual PV data reading
            return {"voltage": 18.2, "current": 1.8, "power": 32.76}  # V  # A  # W

        except Exception as e:
            logger.error(f"Error reading PV data: {str(e)}")
            return None

    async def _read_load_data(self) -> Optional[Dict[str, Any]]:
        """Read load data from the device."""
        try:
            if not self.connection:
                return None

            # Placeholder for actual load data reading
            return {"voltage": 12.1, "current": 0.5, "power": 6.05}  # V  # A  # W

        except Exception as e:
            logger.error(f"Error reading load data: {str(e)}")
            return None

    def _get_mock_data(self) -> RenogyDeviceData:
        """Return mock data for testing when library is not available."""
        data = RenogyDeviceData(device_address=self.device_address)
        data.timestamp = datetime.now()
        data.connection_status = "connected"

        # Mock battery data
        data.battery_voltage = 12.5
        data.battery_current = 2.3
        data.battery_power = 28.75
        data.battery_soc = 85
        data.battery_temperature = 25.5

        # Mock PV data
        data.pv_voltage = 18.2
        data.pv_current = 1.8
        data.pv_power = 32.76

        # Mock load data
        data.load_voltage = 12.1
        data.load_current = 0.5
        data.load_power = 6.05

        return data

    def __str__(self) -> str:
        """String representation of the device."""
        status = "connected" if self.is_connected else "disconnected"
        return f"RenogyDevice(address={self.device_address}, status={status})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"RenogyDevice(device_address='{self.device_address}', "
            f"timeout={self.timeout}, connected={self.is_connected})"
        )


class RenogyDeviceManager:
    """
    Manager class for handling multiple Renogy devices.
    """

    def __init__(self):
        self.devices: Dict[str, RenogyDevice] = {}

    def add_device(self, device_address: str, timeout: int = 10) -> RenogyDevice:
        """
        Add a new device to the manager.

        Args:
            device_address: Bluetooth MAC address of the device
            timeout: Connection timeout in seconds

        Returns:
            RenogyDevice: The created device instance
        """
        device = RenogyDevice(device_address, timeout)
        self.devices[device_address.upper()] = device
        return device

    def get_device(self, device_address: str) -> Optional[RenogyDevice]:
        """Get a device by its address."""
        return self.devices.get(device_address.upper())

    def remove_device(self, device_address: str) -> bool:
        """Remove a device from the manager."""
        device = self.devices.pop(device_address.upper(), None)
        if device and device.is_connected:
            asyncio.create_task(device.disconnect())
        return device is not None

    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all managed devices."""
        results = {}
        for address, device in self.devices.items():
            results[address] = await device.connect()
        return results

    async def disconnect_all(self):
        """Disconnect from all managed devices."""
        for device in self.devices.values():
            if device.is_connected:
                await device.disconnect()

    def list_devices(self) -> list:
        """Get list of all managed device addresses."""
        return list(self.devices.keys())

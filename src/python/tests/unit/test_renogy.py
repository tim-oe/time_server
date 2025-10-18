"""
Test module for Renogy device functionality.

This module contains test cases for the RenogyDevice class and related functionality.
"""

from datetime import datetime

import pytest

from apps.renogy_devices.device import (
    RenogyDevice,
    RenogyDeviceData,
    RenogyDeviceManager,
)


class TestRenogyDevice:
    """Test class for RenogyDevice with device address F8:55:48:17:99:EB."""

    TEST_DEVICE_ADDRESS = "F8:55:48:17:99:EB"

    def setup_method(self):
        """Set up test fixtures."""
        self.device = RenogyDevice(self.TEST_DEVICE_ADDRESS)

    def test_device_initialization(self):
        """Test device initialization with correct address."""
        assert self.device.device_address == self.TEST_DEVICE_ADDRESS.upper()
        assert self.device.timeout == 10
        assert not self.device.is_connected
        assert self.device.connection is None

    def test_device_initialization_with_timeout(self):
        """Test device initialization with custom timeout."""
        device = RenogyDevice(self.TEST_DEVICE_ADDRESS, timeout=30)
        assert device.timeout == 30

    def test_device_address_normalization(self):
        """Test that device address is normalized to uppercase."""
        device = RenogyDevice("f8:55:48:17:99:eb")
        assert device.device_address == "F8:55:48:17:99:EB"

    @pytest.mark.asyncio
    async def test_mock_connection(self):
        """Test connection with mock data (when library not available)."""
        result = await self.device.connect()
        assert result is True
        assert self.device.is_connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test device disconnection."""
        # First connect
        await self.device.connect()
        assert self.device.is_connected is True

        # Then disconnect
        await self.device.disconnect()
        assert self.device.is_connected is False

    @pytest.mark.asyncio
    async def test_read_data_when_disconnected(self):
        """Test reading data when device is not connected."""
        data = await self.device.read_data()

        assert isinstance(data, RenogyDeviceData)
        assert data.device_address == self.TEST_DEVICE_ADDRESS.upper()
        assert data.connection_status == "disconnected"
        assert data.error_message == "Device not connected"
        assert data.timestamp is not None

    @pytest.mark.asyncio
    async def test_read_data_when_connected(self):
        """Test reading data when device is connected."""
        # Connect first
        await self.device.connect()

        # Read data
        data = await self.device.read_data()

        assert isinstance(data, RenogyDeviceData)
        assert data.device_address == self.TEST_DEVICE_ADDRESS.upper()
        assert data.connection_status == "connected"
        assert data.timestamp is not None

        # Check that mock data is present
        assert data.battery_voltage is not None
        assert data.battery_current is not None
        assert data.battery_soc is not None
        assert data.pv_voltage is not None
        assert data.load_voltage is not None

    def test_device_data_to_dict(self):
        """Test conversion of device data to dictionary."""
        data = RenogyDeviceData(
            device_address=self.TEST_DEVICE_ADDRESS,
            battery_voltage=12.5,
            battery_soc=85,
            timestamp=datetime.now(),
        )

        data_dict = data.to_dict()

        assert isinstance(data_dict, dict)
        assert data_dict["device_address"] == self.TEST_DEVICE_ADDRESS
        assert data_dict["battery_voltage"] == 12.5
        assert data_dict["battery_soc"] == 85
        assert "timestamp" in data_dict

    def test_device_string_representation(self):
        """Test string representation of device."""
        device_str = str(self.device)
        assert self.TEST_DEVICE_ADDRESS in device_str
        assert "disconnected" in device_str

        # Test when connected
        self.device.is_connected = True
        device_str = str(self.device)
        assert "connected" in device_str

    def test_device_repr(self):
        """Test detailed string representation."""
        device_repr = repr(self.device)
        assert self.TEST_DEVICE_ADDRESS in device_repr
        assert "timeout=10" in device_repr
        assert "connected=False" in device_repr


class TestRenogyDeviceManager:
    """Test class for RenogyDeviceManager."""

    TEST_DEVICE_ADDRESS = "F8:55:48:17:99:EB"

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = RenogyDeviceManager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        assert isinstance(self.manager.devices, dict)
        assert len(self.manager.devices) == 0

    def test_add_device(self):
        """Test adding a device to the manager."""
        device = self.manager.add_device(self.TEST_DEVICE_ADDRESS)

        assert isinstance(device, RenogyDevice)
        assert device.device_address == self.TEST_DEVICE_ADDRESS.upper()
        assert self.TEST_DEVICE_ADDRESS.upper() in self.manager.devices

    def test_get_device(self):
        """Test getting a device from the manager."""
        # Add device first
        self.manager.add_device(self.TEST_DEVICE_ADDRESS)

        # Get device
        device = self.manager.get_device(self.TEST_DEVICE_ADDRESS)
        assert isinstance(device, RenogyDevice)
        assert device.device_address == self.TEST_DEVICE_ADDRESS.upper()

        # Test getting non-existent device
        non_existent = self.manager.get_device("00:00:00:00:00:00")
        assert non_existent is None

    def test_remove_device(self):
        """Test removing a device from the manager."""
        # Add device first
        self.manager.add_device(self.TEST_DEVICE_ADDRESS)
        assert len(self.manager.devices) == 1

        # Remove device
        result = self.manager.remove_device(self.TEST_DEVICE_ADDRESS)
        assert result is True
        assert len(self.manager.devices) == 0

        # Test removing non-existent device
        result = self.manager.remove_device("00:00:00:00:00:00")
        assert result is False

    def test_list_devices(self):
        """Test listing all devices."""
        # Initially empty
        devices = self.manager.list_devices()
        assert devices == []

        # Add some devices
        self.manager.add_device(self.TEST_DEVICE_ADDRESS)
        self.manager.add_device("AA:BB:CC:DD:EE:FF")

        devices = self.manager.list_devices()
        assert len(devices) == 2
        assert self.TEST_DEVICE_ADDRESS.upper() in devices
        assert "AA:BB:CC:DD:EE:FF" in devices

    @pytest.mark.asyncio
    async def test_connect_all(self):
        """Test connecting to all devices."""
        # Add devices
        self.manager.add_device(self.TEST_DEVICE_ADDRESS)
        self.manager.add_device("AA:BB:CC:DD:EE:FF")

        # Connect to all
        results = await self.manager.connect_all()

        assert isinstance(results, dict)
        assert len(results) == 2
        assert results[self.TEST_DEVICE_ADDRESS.upper()] is True
        assert results["AA:BB:CC:DD:EE:FF"] is True

    @pytest.mark.asyncio
    async def test_disconnect_all(self):
        """Test disconnecting from all devices."""
        # Add and connect devices
        self.manager.add_device(self.TEST_DEVICE_ADDRESS)
        self.manager.add_device("AA:BB:CC:DD:EE:FF")
        await self.manager.connect_all()

        # Verify connected
        for device in self.manager.devices.values():
            assert device.is_connected is True

        # Disconnect all
        await self.manager.disconnect_all()

        # Verify disconnected
        for device in self.manager.devices.values():
            assert device.is_connected is False


class TestRenogyDeviceIntegration:
    """Integration tests for Renogy device functionality."""

    TEST_DEVICE_ADDRESS = "F8:55:48:17:99:EB"

    @pytest.mark.asyncio
    async def test_full_device_lifecycle(self):
        """Test complete device lifecycle: connect -> read -> disconnect."""
        device = RenogyDevice(self.TEST_DEVICE_ADDRESS)

        # Connect
        connected = await device.connect()
        assert connected is True

        # Read data
        data = await device.read_data()
        assert data.connection_status == "connected"
        assert data.battery_voltage is not None

        # Disconnect
        await device.disconnect()
        assert device.is_connected is False

    @pytest.mark.asyncio
    async def test_multiple_reads(self):
        """Test multiple data reads from the same device."""
        device = RenogyDevice(self.TEST_DEVICE_ADDRESS)
        await device.connect()

        # Read data multiple times
        data1 = await device.read_data()
        data2 = await device.read_data()

        # Both should be successful
        assert data1.connection_status == "connected"
        assert data2.connection_status == "connected"

        # Timestamps should be different
        assert data1.timestamp != data2.timestamp

        await device.disconnect()

    def test_device_data_validation(self):
        """Test device data structure validation."""
        # Test with all fields
        data = RenogyDeviceData(
            device_address=self.TEST_DEVICE_ADDRESS,
            battery_voltage=12.5,
            battery_current=2.3,
            battery_power=28.75,
            battery_soc=85,
            battery_temperature=25.5,
            pv_voltage=18.2,
            pv_current=1.8,
            pv_power=32.76,
            load_voltage=12.1,
            load_current=0.5,
            load_power=6.05,
            timestamp=datetime.now(),
            connection_status="connected",
        )

        # Convert to dict and verify all fields
        data_dict = data.to_dict()
        expected_fields = [
            "device_address",
            "battery_voltage",
            "battery_current",
            "battery_power",
            "battery_soc",
            "battery_temperature",
            "pv_voltage",
            "pv_current",
            "pv_power",
            "load_voltage",
            "load_current",
            "load_power",
            "timestamp",
            "connection_status",
            "error_message",
        ]

        for field in expected_fields:
            assert field in data_dict


# Pytest fixtures for common test data
@pytest.fixture
def test_device_address():
    """Fixture providing the test device address."""
    return "F8:55:48:17:99:EB"


@pytest.fixture
def renogy_device(test_device_address):
    """Fixture providing a RenogyDevice instance."""
    return RenogyDevice(test_device_address)


@pytest.fixture
def renogy_manager():
    """Fixture providing a RenogyDeviceManager instance."""
    return RenogyDeviceManager()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])

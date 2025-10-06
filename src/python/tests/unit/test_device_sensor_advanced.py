"""
Advanced Device and Sensor Tests

Tests for advanced functionality and edge cases in device and sensor classes.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch, mock_open
from datetime import datetime

from apps.renogy_devices.device import (
    RenogyDevice,
    RenogyDeviceData,
    RenogyDeviceManager,
)
from apps.ds18b20_sensors.sensor import (
    DS18B20Sensor,
    DS18B20SensorManager,
    TemperatureReading,
    discover_all_ds18b20_sensors,
    create_sensor_from_id,
)


class TestRenogyDeviceAdvanced:
    """Advanced tests for RenogyDevice class."""

    @pytest.mark.asyncio
    async def test_connect_with_renogy_library_available(self):
        """Test connection when renogy library is available."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        
        with patch('apps.renogy_devices.device.RENOGY_AVAILABLE', True), \
             patch('apps.renogy_devices.device.RenogyModbus') as mock_renogy:
            
            mock_connection = Mock()
            mock_renogy.return_value = mock_connection
            
            # Mock the _test_connection method
            with patch.object(device, '_test_connection', new_callable=AsyncMock) as mock_test:
                mock_test.return_value = None
                
                result = await device.connect()
                
                assert result is True
                assert device.is_connected is True
                mock_renogy.assert_called_once_with(
                    device="F8:55:48:17:99:EB",
                    baudrate=9600,
                    timeout=10
                )
                mock_test.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_with_renogy_library_unavailable(self):
        """Test connection when renogy library is not available."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        
        with patch('apps.renogy_devices.device.RENOGY_AVAILABLE', False):
            result = await device.connect()
            
            assert result is True  # Mock connection succeeds
            assert device.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        """Test connection failure."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        
        with patch('apps.renogy_devices.device.RENOGY_AVAILABLE', True), \
             patch('apps.renogy_devices.device.RenogyModbus') as mock_renogy:
            
            mock_renogy.side_effect = Exception("Connection failed")
            
            result = await device.connect()
            
            assert result is False
            assert device.is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect_with_connection(self):
        """Test disconnection when connected."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.is_connected = True
        device.connection = Mock()
        device.connection.close = Mock()
        
        await device.disconnect()
        
        assert device.is_connected is False
        assert device.connection is None

    @pytest.mark.asyncio
    async def test_disconnect_without_connection(self):
        """Test disconnection when not connected."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.is_connected = False
        device.connection = None
        
        await device.disconnect()
        
        assert device.is_connected is False

    @pytest.mark.asyncio
    async def test_read_data_when_connected_with_library(self):
        """Test reading data when connected with library available."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.is_connected = True
        
        with patch('apps.renogy_devices.device.RENOGY_AVAILABLE', True), \
             patch.object(device, '_read_battery_data', new_callable=AsyncMock) as mock_battery, \
             patch.object(device, '_read_pv_data', new_callable=AsyncMock) as mock_pv, \
             patch.object(device, '_read_load_data', new_callable=AsyncMock) as mock_load:
            
            mock_battery.return_value = {
                'voltage': 12.5, 'current': 2.3, 'power': 28.75, 'soc': 85, 'temperature': 25.5
            }
            mock_pv.return_value = {
                'voltage': 18.2, 'current': 1.8, 'power': 32.76
            }
            mock_load.return_value = {
                'voltage': 12.1, 'current': 0.5, 'power': 6.05
            }
            
            data = await device.read_data()
            
            assert data.connection_status == "connected"
            assert data.battery_voltage == 12.5
            assert data.battery_soc == 85
            assert data.pv_voltage == 18.2
            assert data.load_voltage == 12.1
            assert data.error_message is None

    @pytest.mark.asyncio
    async def test_read_data_with_errors(self):
        """Test reading data with errors."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.is_connected = True
        
        with patch('apps.renogy_devices.device.RENOGY_AVAILABLE', True), \
             patch.object(device, '_read_battery_data', new_callable=AsyncMock) as mock_battery:
            
            mock_battery.side_effect = Exception("Read error")
            
            data = await device.read_data()
            
            assert data.connection_status == "error"
            assert data.error_message == "Read error"

    @pytest.mark.asyncio
    async def test_read_battery_data_success(self):
        """Test successful battery data reading."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.connection = Mock()
        
        data = await device._read_battery_data()
        
        assert data is not None
        assert 'voltage' in data
        assert 'current' in data
        assert 'power' in data
        assert 'soc' in data
        assert 'temperature' in data

    @pytest.mark.asyncio
    async def test_read_battery_data_no_connection(self):
        """Test battery data reading without connection."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.connection = None
        
        data = await device._read_battery_data()
        
        assert data is None

    @pytest.mark.asyncio
    async def test_read_pv_data_success(self):
        """Test successful PV data reading."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.connection = Mock()
        
        data = await device._read_pv_data()
        
        assert data is not None
        assert 'voltage' in data
        assert 'current' in data
        assert 'power' in data

    @pytest.mark.asyncio
    async def test_read_load_data_success(self):
        """Test successful load data reading."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.connection = Mock()
        
        data = await device._read_load_data()
        
        assert data is not None
        assert 'voltage' in data
        assert 'current' in data
        assert 'power' in data

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful connection test."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.connection = Mock()
        
        # Should not raise an exception
        await device._test_connection()

    @pytest.mark.asyncio
    async def test_test_connection_no_connection(self):
        """Test connection test without connection."""
        device = RenogyDevice("F8:55:48:17:99:EB")
        device.connection = None
        
        with pytest.raises(Exception, match="No connection established"):
            await device._test_connection()


class TestRenogyDeviceManagerAdvanced:
    """Advanced tests for RenogyDeviceManager class."""

    @pytest.mark.asyncio
    async def test_connect_all_devices(self):
        """Test connecting to all devices."""
        manager = RenogyDeviceManager()
        device1 = manager.add_device("F8:55:48:17:99:EB")
        device2 = manager.add_device("F8:55:48:17:99:EC")
        
        with patch.object(device1, 'connect', new_callable=AsyncMock) as mock_connect1, \
             patch.object(device2, 'connect', new_callable=AsyncMock) as mock_connect2:
            
            mock_connect1.return_value = True
            mock_connect2.return_value = False
            
            results = await manager.connect_all()
            
            assert results["F8:55:48:17:99:EB"] is True
            assert results["F8:55:48:17:99:EC"] is False
            mock_connect1.assert_called_once()
            mock_connect2.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_all_devices(self):
        """Test disconnecting from all devices."""
        manager = RenogyDeviceManager()
        device1 = manager.add_device("F8:55:48:17:99:EB")
        device2 = manager.add_device("F8:55:48:17:99:EC")
        device1.is_connected = True
        device2.is_connected = True
        
        with patch.object(device1, 'disconnect', new_callable=AsyncMock) as mock_disconnect1, \
             patch.object(device2, 'disconnect', new_callable=AsyncMock) as mock_disconnect2:
            
            await manager.disconnect_all()
            
            mock_disconnect1.assert_called_once()
            mock_disconnect2.assert_called_once()

    def test_remove_device_with_connection(self):
        """Test removing a device that is connected."""
        manager = RenogyDeviceManager()
        device = manager.add_device("F8:55:48:17:99:EB")
        device.is_connected = True
        
        with patch('asyncio.create_task') as mock_task:
            result = manager.remove_device("F8:55:48:17:99:EB")
            
            assert result is True
            assert "F8:55:48:17:99:EB" not in manager.devices
            mock_task.assert_called_once()

    def test_remove_nonexistent_device(self):
        """Test removing a device that doesn't exist."""
        manager = RenogyDeviceManager()
        
        result = manager.remove_device("00:00:00:00:00:00")
        
        assert result is False


class TestDS18B20SensorAdvanced:
    """Advanced tests for DS18B20Sensor class."""

    def test_initialize_1wire_interface(self):
        """Test 1-Wire interface initialization."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        with patch('os.system') as mock_system:
            sensor._initialize_1wire_interface()
            
            assert mock_system.call_count == 2
            mock_system.assert_any_call("modprobe w1-gpio")
            mock_system.assert_any_call("modprobe w1-therm")

    def test_read_raw_data_success(self):
        """Test successful raw data reading."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        mock_data = ["YES\n", "t=25000\n"]
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=''.join(mock_data))):
            
            result = sensor._read_raw_data()
            
            assert result == mock_data

    def test_read_raw_data_file_not_found(self):
        """Test raw data reading when file doesn't exist."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        with patch('pathlib.Path.exists', return_value=False):
            result = sensor._read_raw_data()
            
            assert result is None

    def test_read_raw_data_read_error(self):
        """Test raw data reading with read error."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', side_effect=IOError("Read error")):
            
            result = sensor._read_raw_data()
            
            assert result is None

    def test_parse_temperature_valid_data(self):
        """Test parsing valid temperature data."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        lines = ["YES\n", "t=25000\n"]
        result = sensor._parse_temperature(lines)
        
        assert result == 25.0

    def test_parse_temperature_invalid_data(self):
        """Test parsing invalid temperature data."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        lines = ["NO\n", "t=25000\n"]
        result = sensor._parse_temperature(lines)
        
        assert result is None

    def test_parse_temperature_missing_temperature(self):
        """Test parsing data with missing temperature."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        lines = ["YES\n", "no temperature here\n"]
        result = sensor._parse_temperature(lines)
        
        assert result is None

    def test_parse_temperature_invalid_format(self):
        """Test parsing data with invalid temperature format."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        lines = ["YES\n", "t=invalid\n"]
        result = sensor._parse_temperature(lines)
        
        assert result is None

    def test_read_temperature_with_retries(self):
        """Test temperature reading with retries."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch.object(sensor, '_read_raw_data') as mock_read, \
             patch.object(sensor, '_parse_temperature') as mock_parse, \
             patch('time.sleep'):
            
            # First call returns None, second call returns valid data
            mock_read.side_effect = [None, ["YES\n", "t=25000\n"], ["YES\n", "t=25000\n"]]
            mock_parse.side_effect = [None, 25.0, 25.0]
            
            result = sensor.read_temperature(max_retries=3)
            
            assert result.temperature_celsius == 25.0
            assert result.temperature_fahrenheit == 77.0
            assert result.is_valid is True
            assert mock_read.call_count >= 2

    def test_read_temperature_all_retries_fail(self):
        """Test temperature reading when all retries fail."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch.object(sensor, '_read_raw_data', return_value=None), \
             patch('time.sleep'):
            
            result = sensor.read_temperature(max_retries=2)
            
            assert result.is_valid is False
            assert "Failed to read sensor data" in result.error_message

    def test_read_temperature_parse_failure(self):
        """Test temperature reading with parse failure."""
        sensor = DS18B20Sensor("28-0123456789ab", "Test Sensor")
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch.object(sensor, '_read_raw_data', return_value=["YES\n", "t=25000\n"]), \
             patch.object(sensor, '_parse_temperature', return_value=None), \
             patch('time.sleep'):
            
            result = sensor.read_temperature(max_retries=2)
            
            assert result.is_valid is False
            assert "Failed to read valid temperature after 2 attempts" in result.error_message


class TestDS18B20SensorManagerAdvanced:
    """Advanced tests for DS18B20SensorManager class."""

    def test_initialize_1wire_interface(self):
        """Test 1-Wire interface initialization in manager."""
        manager = DS18B20SensorManager()
        
        with patch('os.system') as mock_system:
            manager._initialize_1wire_interface()
            
            assert mock_system.call_count == 2
            mock_system.assert_any_call("modprobe w1-gpio")
            mock_system.assert_any_call("modprobe w1-therm")

    def test_discover_sensors_with_glob(self):
        """Test sensor discovery with glob."""
        manager = DS18B20SensorManager()
        
        with patch('glob.glob') as mock_glob:
            mock_glob.return_value = [
                "/sys/bus/w1/devices/28-0123456789ab",
                "/sys/bus/w1/devices/28-0123456789cd"
            ]
            
            result = manager.discover_sensors()
            
            assert result == ["28-0123456789ab", "28-0123456789cd"]
            mock_glob.assert_called_once_with("/sys/bus/w1/devices/28*")

    def test_discover_sensors_with_error(self):
        """Test sensor discovery with error."""
        manager = DS18B20SensorManager()
        
        with patch('glob.glob', side_effect=Exception("Discovery error")):
            result = manager.discover_sensors()
            
            assert result == []

    def test_read_available_temperatures(self):
        """Test reading temperatures from available sensors only."""
        manager = DS18B20SensorManager()
        sensor1 = manager.add_sensor("28-0123456789ab", "Sensor 1")
        sensor2 = manager.add_sensor("28-0123456789cd", "Sensor 2")
        
        with patch.object(sensor1, 'is_available', return_value=True), \
             patch.object(sensor2, 'is_available', return_value=False), \
             patch.object(sensor1, 'read_temperature') as mock_read:
            
            mock_reading = TemperatureReading(
                sensor_id="28-0123456789ab",
                sensor_name="Sensor 1",
                temperature_celsius=25.0,
                temperature_fahrenheit=77.0,
                timestamp=datetime.now()
            )
            mock_read.return_value = mock_reading
            
            result = manager.read_available_temperatures()
            
            assert len(result) == 1
            assert result[0].sensor_id == "28-0123456789ab"
            mock_read.assert_called_once()

    def test_get_sensor_summary(self):
        """Test getting sensor summary."""
        manager = DS18B20SensorManager()
        sensor1 = manager.add_sensor("28-0123456789ab", "Sensor 1")
        sensor2 = manager.add_sensor("28-0123456789cd", "Sensor 2")
        
        with patch.object(sensor1, 'is_available', return_value=True), \
             patch.object(sensor2, 'is_available', return_value=False):
            
            summary = manager.get_sensor_summary()
            
            assert summary["total_sensors"] == 2
            assert summary["available_sensors"] == 1
            assert summary["unavailable_sensors"] == 1
            assert len(summary["sensors"]) == 2


class TestUtilityFunctionsAdvanced:
    """Advanced tests for utility functions."""

    def test_discover_all_ds18b20_sensors_with_custom_base_dir(self):
        """Test discovering sensors with custom base directory."""
        with patch('apps.ds18b20_sensors.sensor.DS18B20SensorManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.discover_sensors.return_value = ["28-0123456789ab"]
            mock_manager_class.return_value = mock_manager
            
            result = discover_all_ds18b20_sensors("/custom/path/")
            
            assert result == ["28-0123456789ab"]
            mock_manager_class.assert_called_once_with("/custom/path/")

    def test_create_sensor_from_id_with_custom_name(self):
        """Test creating sensor from ID with custom name."""
        sensor = create_sensor_from_id("28-0123456789ab", "Custom Name")
        
        assert sensor.sensor_id == "28-0123456789ab"
        assert sensor.sensor_name == "Custom Name"

    def test_create_sensor_from_id_with_default_name(self):
        """Test creating sensor from ID with default name."""
        sensor = create_sensor_from_id("28-0123456789ab")
        
        assert sensor.sensor_id == "28-0123456789ab"
        assert sensor.sensor_name == "Sensor 28-0123456789ab"


class TestRenogyDeviceDataAdvanced:
    """Advanced tests for RenogyDeviceData class."""

    def test_to_dict_with_all_fields(self):
        """Test converting to dictionary with all fields."""
        timestamp = datetime.now()
        data = RenogyDeviceData(
            device_address="F8:55:48:17:99:EB",
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
            timestamp=timestamp,
            connection_status="connected",
            error_message=None
        )
        
        result = data.to_dict()
        
        assert result["device_address"] == "F8:55:48:17:99:EB"
        assert result["battery_voltage"] == 12.5
        assert result["battery_soc"] == 85
        assert result["pv_voltage"] == 18.2
        assert result["load_voltage"] == 12.1
        assert result["timestamp"] == timestamp.isoformat()
        assert result["connection_status"] == "connected"
        assert result["error_message"] is None

    def test_to_dict_with_none_timestamp(self):
        """Test converting to dictionary with None timestamp."""
        data = RenogyDeviceData(
            device_address="F8:55:48:17:99:EB",
            timestamp=None
        )
        
        result = data.to_dict()
        
        assert result["timestamp"] is None


class TestTemperatureReadingAdvanced:
    """Advanced tests for TemperatureReading class."""

    def test_to_dict_with_error(self):
        """Test converting to dictionary with error."""
        reading = TemperatureReading(
            sensor_id="28-0123456789ab",
            sensor_name="Test Sensor",
            temperature_celsius=0.0,
            temperature_fahrenheit=32.0,
            timestamp=datetime.now(),
            error_message="Sensor not found",
            is_valid=False
        )
        
        result = reading.to_dict()
        
        assert result["sensor_id"] == "28-0123456789ab"
        assert result["sensor_name"] == "Test Sensor"
        assert result["temperature_celsius"] == 0.0
        assert result["temperature_fahrenheit"] == 32.0
        assert result["error_message"] == "Sensor not found"
        assert result["is_valid"] is False

    def test_to_dict_temperature_rounding(self):
        """Test temperature rounding in to_dict."""
        reading = TemperatureReading(
            sensor_id="28-0123456789ab",
            sensor_name="Test Sensor",
            temperature_celsius=25.123456,
            temperature_fahrenheit=77.222222,
            timestamp=datetime.now()
        )
        
        result = reading.to_dict()
        
        assert result["temperature_celsius"] == 25.12
        assert result["temperature_fahrenheit"] == 77.22

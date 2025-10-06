# Renogy Device Module Documentation

## Overview

The Renogy Device Module provides functionality to communicate with Renogy solar charge controllers and battery monitors via Bluetooth. This module includes a comprehensive API for device management, data reading, and testing.

## Features

- **Bluetooth Communication**: Connect to Renogy devices via Bluetooth
- **Data Reading**: Read battery, PV (solar panel), and load data
- **Device Management**: Add, remove, connect, and disconnect devices
- **Mock Data Support**: Works with mock data when hardware is not available
- **REST API**: Full REST API endpoints for device operations
- **Comprehensive Testing**: Complete test suite with the specified device address

## Module Structure

### Core Classes

#### `RenogyDevice`
Main class for handling individual Renogy devices.

**Constructor:**
```python
device = RenogyDevice(device_address="F8:55:48:17:99:EB", timeout=10)
```

**Key Methods:**
- `connect()`: Connect to the device
- `disconnect()`: Disconnect from the device
- `read_data()`: Read all device data

#### `RenogyDeviceData`
Data structure for device information.

**Fields:**
- `device_address`: Bluetooth MAC address
- `battery_voltage`: Battery voltage (V)
- `battery_current`: Battery current (A)
- `battery_power`: Battery power (W)
- `battery_soc`: State of charge (%)
- `battery_temperature`: Battery temperature (°C)
- `pv_voltage`: Solar panel voltage (V)
- `pv_current`: Solar panel current (A)
- `pv_power`: Solar panel power (W)
- `load_voltage`: Load voltage (V)
- `load_current`: Load current (A)
- `load_power`: Load power (W)
- `timestamp`: Data timestamp
- `connection_status`: Connection status
- `error_message`: Error message if any

#### `RenogyDeviceManager`
Manager class for handling multiple devices.

**Key Methods:**
- `add_device(address, timeout)`: Add a new device
- `get_device(address)`: Get device by address
- `remove_device(address)`: Remove device
- `connect_all()`: Connect to all devices
- `disconnect_all()`: Disconnect from all devices
- `list_devices()`: List all managed devices

## API Endpoints

### Device Management

#### List Devices
**GET** `/api/renogy/devices/`

Returns list of all managed devices.

**Response:**
```json
{
    "devices": [
        {
            "address": "F8:55:48:17:99:EB",
            "connected": true,
            "timeout": 10
        }
    ],
    "total_count": 1
}
```

#### Add Device
**POST** `/api/renogy/devices/add/`

Add a new device to the manager.

**Request:**
```json
{
    "device_address": "F8:55:48:17:99:EB",
    "timeout": 10
}
```

**Response:**
```json
{
    "message": "Device added successfully",
    "device_address": "F8:55:48:17:99:EB",
    "timeout": 10
}
```

#### Remove Device
**DELETE** `/api/renogy/devices/{device_address}/`

Remove a device from the manager.

**Response:**
```json
{
    "message": "Device removed successfully",
    "device_address": "F8:55:48:17:99:EB"
}
```

### Device Operations

#### Connect to Device
**POST** `/api/renogy/devices/{device_address}/connect/`

Connect to a specific device.

**Response:**
```json
{
    "message": "Device connected successfully",
    "device_address": "F8:55:48:17:99:EB",
    "status": "connected"
}
```

#### Disconnect from Device
**POST** `/api/renogy/devices/{device_address}/disconnect/`

Disconnect from a specific device.

**Response:**
```json
{
    "message": "Device disconnected successfully",
    "device_address": "F8:55:48:17:99:EB",
    "status": "disconnected"
}
```

#### Get Device Data
**GET** `/api/renogy/devices/{device_address}/data/`

Read data from a specific device.

**Response:**
```json
{
    "device_address": "F8:55:48:17:99:EB",
    "battery_voltage": 12.5,
    "battery_current": 2.3,
    "battery_power": 28.75,
    "battery_soc": 85,
    "battery_temperature": 25.5,
    "pv_voltage": 18.2,
    "pv_current": 1.8,
    "pv_power": 32.76,
    "load_voltage": 12.1,
    "load_current": 0.5,
    "load_power": 6.05,
    "timestamp": "2025-10-05T22:38:57.691912",
    "connection_status": "connected",
    "error_message": null
}
```

#### Get Device Status
**GET** `/api/renogy/devices/{device_address}/status/`

Get connection status of a device.

**Response:**
```json
{
    "device_address": "F8:55:48:17:99:EB",
    "connected": true,
    "timeout": 10,
    "status": "connected"
}
```

### Bulk Operations

#### Connect All Devices
**POST** `/api/renogy/connect-all/`

Connect to all managed devices.

**Response:**
```json
{
    "message": "Connection attempt completed",
    "results": {
        "F8:55:48:17:99:EB": true
    },
    "total_devices": 1,
    "successful_connections": 1
}
```

#### Disconnect All Devices
**POST** `/api/renogy/disconnect-all/`

Disconnect from all managed devices.

**Response:**
```json
{
    "message": "All devices disconnected successfully",
    "total_devices": 1
}
```

#### Get All Device Data
**GET** `/api/renogy/all-data/`

Get data from all connected devices.

**Response:**
```json
{
    "devices": {
        "F8:55:48:17:99:EB": {
            "device_address": "F8:55:48:17:99:EB",
            "battery_voltage": 12.5,
            "battery_current": 2.3,
            "battery_power": 28.75,
            "battery_soc": 85,
            "battery_temperature": 25.5,
            "pv_voltage": 18.2,
            "pv_current": 1.8,
            "pv_power": 32.76,
            "load_voltage": 12.1,
            "load_current": 0.5,
            "load_power": 6.05,
            "timestamp": "2025-10-05T22:38:57.691912",
            "connection_status": "connected",
            "error_message": null
        }
    },
    "total_devices": 1,
    "connected_devices": 1
}
```

## Testing

### Test Class: `TestRenogyDevice`

The test class includes comprehensive tests for the device with address `F8:55:48:17:99:EB`:

#### Test Methods:
- `test_device_initialization()`: Test device initialization
- `test_device_initialization_with_timeout()`: Test custom timeout
- `test_device_address_normalization()`: Test address normalization
- `test_mock_connection()`: Test connection with mock data
- `test_disconnect()`: Test device disconnection
- `test_read_data_when_disconnected()`: Test reading when disconnected
- `test_read_data_when_connected()`: Test reading when connected
- `test_device_data_to_dict()`: Test data serialization
- `test_device_string_representation()`: Test string representation
- `test_device_repr()`: Test detailed representation

#### Test Manager: `TestRenogyDeviceManager`

Tests for the device manager:

- `test_manager_initialization()`: Test manager setup
- `test_add_device()`: Test adding devices
- `test_get_device()`: Test retrieving devices
- `test_remove_device()`: Test removing devices
- `test_list_devices()`: Test listing devices
- `test_connect_all()`: Test connecting to all devices
- `test_disconnect_all()`: Test disconnecting from all devices

#### Integration Tests: `TestRenogyDeviceIntegration`

End-to-end tests:

- `test_full_device_lifecycle()`: Complete device lifecycle
- `test_multiple_reads()`: Multiple data reads
- `test_device_data_validation()`: Data structure validation

### Running Tests

```bash
# Run all Renogy tests
poetry run pytest api/test_renogy.py -v

# Run specific test class
poetry run pytest api/test_renogy.py::TestRenogyDevice -v

# Run with coverage
poetry run pytest api/test_renogy.py --cov=api.renogy_device
```

## Usage Examples

### Basic Usage

```python
from api.renogy_device import RenogyDevice

# Create device instance
device = RenogyDevice("F8:55:48:17:99:EB")

# Connect to device
await device.connect()

# Read data
data = await device.read_data()
print(f"Battery SOC: {data.battery_soc}%")
print(f"PV Power: {data.pv_power}W")

# Disconnect
await device.disconnect()
```

### Using the Manager

```python
from api.renogy_device import RenogyDeviceManager

# Create manager
manager = RenogyDeviceManager()

# Add device
device = manager.add_device("F8:55:48:17:99:EB")

# Connect to all devices
results = await manager.connect_all()

# Read data from all devices
for address in manager.list_devices():
    device = manager.get_device(address)
    if device.is_connected:
        data = await device.read_data()
        print(f"Device {address}: {data.battery_soc}% SOC")
```

### API Usage with curl

```bash
# Add device
curl -X POST http://localhost:8000/api/renogy/devices/add/ \
  -H "Content-Type: application/json" \
  -d '{"device_address": "F8:55:48:17:99:EB"}'

# Connect to device
curl -X POST http://localhost:8000/api/renogy/devices/F8:55:48:17:99:EB/connect/

# Read device data
curl http://localhost:8000/api/renogy/devices/F8:55:48:17:99:EB/data/

# List all devices
curl http://localhost:8000/api/renogy/devices/
```

## Dependencies

- `renogy-modbus-lib-python`: Renogy Modbus communication library
- `pytest-asyncio`: Async test support
- `bleak`: Bluetooth Low Energy communication
- `pyserial`: Serial communication support

## Error Handling

The module includes comprehensive error handling:

- **Connection Errors**: Handled with appropriate error messages
- **Data Reading Errors**: Graceful degradation with error status
- **Invalid Addresses**: Validation with clear error messages
- **Device Not Found**: 404 responses for missing devices
- **Already Connected/Disconnected**: Appropriate status messages

## Mock Data

When the `renogy-modbus-lib-python` library is not available or for testing purposes, the module provides realistic mock data:

- Battery voltage: 12.5V
- Battery current: 2.3A
- Battery SOC: 85%
- PV voltage: 18.2V
- PV current: 1.8A
- Load voltage: 12.1V
- Load current: 0.5A

## Configuration

### Environment Variables

No specific environment variables are required. The module uses Django settings for configuration.

### Settings

The module integrates with Django REST Framework settings for permissions and authentication.

## Security Considerations

- **Bluetooth Security**: Ensure proper Bluetooth pairing and security
- **API Authentication**: Consider adding authentication for production use
- **Input Validation**: All device addresses are validated
- **Error Information**: Error messages don't expose sensitive system information

## Performance

- **Async Operations**: All I/O operations are asynchronous
- **Connection Pooling**: Devices maintain persistent connections
- **Efficient Data Reading**: Batch operations for multiple devices
- **Memory Management**: Proper cleanup of connections and resources

## Troubleshooting

### Common Issues

1. **Device Not Found**: Ensure the device address is correct and the device is in pairing mode
2. **Connection Timeout**: Increase the timeout value or check Bluetooth connectivity
3. **Permission Denied**: Ensure the application has Bluetooth permissions
4. **Library Not Available**: The module will use mock data if the library is not installed

### Debug Mode

Enable debug logging to see detailed connection and data reading information:

```python
import logging
logging.getLogger('api.renogy_device').setLevel(logging.DEBUG)
```

## Future Enhancements

- **Real-time Data Streaming**: WebSocket support for real-time data
- **Data Logging**: Persistent storage of device data
- **Alert System**: Notifications for critical battery levels
- **Multi-protocol Support**: Support for other communication protocols
- **Device Discovery**: Automatic device discovery and pairing

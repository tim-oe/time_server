"""
Renogy Device API Views

This module provides REST API endpoints for interacting with Renogy devices.
"""

import asyncio

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .renogy_device import RenogyDeviceManager

# Global device manager instance
device_manager = RenogyDeviceManager()


@extend_schema(
    summary="List Renogy devices",
    description="Retrieve a list of all managed Renogy devices with their connection status",
    tags=["Renogy Devices"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "devices": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "address": {
                                "type": "string",
                                "example": "F8:55:48:17:99:EB",
                            },
                            "connected": {"type": "boolean", "example": True},
                            "timeout": {"type": "integer", "example": 10},
                        },
                    },
                },
                "total_count": {"type": "integer", "example": 1},
            },
        }
    },
)
@api_view(["GET"])
def renogy_device_list(request):
    """List all managed Renogy devices."""
    devices = device_manager.list_devices()
    device_info = []

    for address in devices:
        device = device_manager.get_device(address)
        device_info.append(
            {
                "address": address,
                "connected": device.is_connected if device else False,
                "timeout": device.timeout if device else None,
            }
        )

    return Response({"devices": device_info, "total_count": len(devices)})


@api_view(["POST"])
def renogy_device_add(request):
    """Add a new Renogy device."""
    device_address = request.data.get("device_address")
    timeout = request.data.get("timeout", 10)

    if not device_address:
        return Response(
            {"error": "device_address is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Validate device address format (basic validation)
    if not _is_valid_bluetooth_address(device_address):
        return Response(
            {"error": "Invalid Bluetooth address format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if device already exists
    if device_manager.get_device(device_address):
        return Response(
            {"error": "Device already exists"}, status=status.HTTP_409_CONFLICT
        )

    # Add device
    device = device_manager.add_device(device_address, timeout)

    return Response(
        {
            "message": "Device added successfully",
            "device_address": device.device_address,
            "timeout": device.timeout,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
def renogy_device_remove(request, device_address):
    """Remove a Renogy device."""
    if not device_manager.get_device(device_address):
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    # Disconnect and remove device
    asyncio.create_task(_disconnect_device_async(device_address))
    device_manager.remove_device(device_address)

    return Response(
        {"message": "Device removed successfully", "device_address": device_address}
    )


@api_view(["POST"])
def renogy_device_connect(request, device_address):
    """Connect to a specific Renogy device."""
    device = device_manager.get_device(device_address)
    if not device:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    if device.is_connected:
        return Response(
            {
                "message": "Device already connected",
                "device_address": device_address,
                "status": "connected",
            }
        )

    # Connect to device
    try:
        connected = asyncio.run(device.connect())
        if connected:
            return Response(
                {
                    "message": "Device connected successfully",
                    "device_address": device_address,
                    "status": "connected",
                }
            )
        else:
            return Response(
                {
                    "error": "Failed to connect to device",
                    "device_address": device_address,
                    "status": "disconnected",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    except Exception as e:
        return Response(
            {
                "error": f"Connection error: {str(e)}",
                "device_address": device_address,
                "status": "error",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def renogy_device_disconnect(request, device_address):
    """Disconnect from a specific Renogy device."""
    device = device_manager.get_device(device_address)
    if not device:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    if not device.is_connected:
        return Response(
            {
                "message": "Device already disconnected",
                "device_address": device_address,
                "status": "disconnected",
            }
        )

    # Disconnect from device
    try:
        asyncio.run(device.disconnect())
        return Response(
            {
                "message": "Device disconnected successfully",
                "device_address": device_address,
                "status": "disconnected",
            }
        )
    except Exception as e:
        return Response(
            {
                "error": f"Disconnection error: {str(e)}",
                "device_address": device_address,
                "status": "error",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def renogy_device_data(request, device_address):
    """Get data from a specific Renogy device."""
    device = device_manager.get_device(device_address)
    if not device:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    # Read data from device
    try:
        data = asyncio.run(device.read_data())
        return Response(data.to_dict())
    except Exception as e:
        return Response(
            {
                "error": f"Error reading device data: {str(e)}",
                "device_address": device_address,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def renogy_device_status(request, device_address):
    """Get status of a specific Renogy device."""
    device = device_manager.get_device(device_address)
    if not device:
        return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            "device_address": device_address,
            "connected": device.is_connected,
            "timeout": device.timeout,
            "status": "connected" if device.is_connected else "disconnected",
        }
    )


@api_view(["POST"])
def renogy_connect_all(request):
    """Connect to all managed Renogy devices."""
    try:
        results = asyncio.run(device_manager.connect_all())
        return Response(
            {
                "message": "Connection attempt completed",
                "results": results,
                "total_devices": len(results),
                "successful_connections": sum(
                    1 for success in results.values() if success
                ),
            }
        )
    except Exception as e:
        return Response(
            {"error": f"Error connecting to devices: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def renogy_disconnect_all(request):
    """Disconnect from all managed Renogy devices."""
    try:
        asyncio.run(device_manager.disconnect_all())
        return Response(
            {
                "message": "All devices disconnected successfully",
                "total_devices": len(device_manager.devices),
            }
        )
    except Exception as e:
        return Response(
            {"error": f"Error disconnecting from devices: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def renogy_all_data(request):
    """Get data from all connected Renogy devices."""
    devices = device_manager.list_devices()
    all_data = {}

    for address in devices:
        device = device_manager.get_device(address)
        if device and device.is_connected:
            try:
                data = asyncio.run(device.read_data())
                all_data[address] = data.to_dict()
            except Exception as e:
                all_data[address] = {
                    "error": f"Error reading data: {str(e)}",
                    "device_address": address,
                    "connection_status": "error",
                }
        else:
            all_data[address] = {
                "error": "Device not connected",
                "device_address": address,
                "connection_status": "disconnected",
            }

    return Response(
        {
            "devices": all_data,
            "total_devices": len(devices),
            "connected_devices": sum(
                1 for device in device_manager.devices.values() if device.is_connected
            ),
        }
    )


@extend_schema_view(
    list=extend_schema(
        summary="List Renogy devices",
        description="Retrieve a list of all managed Renogy devices",
        tags=["Renogy Devices"],
    ),
    create=extend_schema(
        summary="Add Renogy device",
        description="Add a new Renogy device to the manager",
        tags=["Renogy Devices"],
    ),
    destroy=extend_schema(
        summary="Remove Renogy device",
        description="Remove a Renogy device from the manager",
        tags=["Renogy Devices"],
    ),
)
class RenogyDeviceViewSet(viewsets.ViewSet):
    """ViewSet for Renogy device operations."""

    permission_classes = [AllowAny]

    def list(self, request):
        """List all devices."""
        return renogy_device_list(request)

    def create(self, request):
        """Add a new device."""
        return renogy_device_add(request)

    def destroy(self, request, pk=None):
        """Remove a device."""
        return renogy_device_remove(request, pk)

    @action(detail=True, methods=["post"])
    def connect(self, request, pk=None):
        """Connect to a device."""
        return renogy_device_connect(request, pk)

    @action(detail=True, methods=["post"])
    def disconnect(self, request, pk=None):
        """Disconnect from a device."""
        return renogy_device_disconnect(request, pk)

    @action(detail=True, methods=["get"])
    def data(self, request, pk=None):
        """Get device data."""
        return renogy_device_data(request, pk)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        """Get device status."""
        return renogy_device_status(request, pk)

    @action(detail=False, methods=["post"])
    def connect_all(self, request):
        """Connect to all devices."""
        return renogy_connect_all(request)

    @action(detail=False, methods=["post"])
    def disconnect_all(self, request):
        """Disconnect from all devices."""
        return renogy_disconnect_all(request)

    @action(detail=False, methods=["get"])
    def all_data(self, request):
        """Get data from all devices."""
        return renogy_all_data(request)


# Helper functions
def _is_valid_bluetooth_address(address: str) -> bool:
    """Validate Bluetooth address format."""
    if not address:
        return False

    # Basic validation: should be in format XX:XX:XX:XX:XX:XX
    parts = address.split(":")
    if len(parts) != 6:
        return False

    for part in parts:
        if len(part) != 2:
            return False
        try:
            int(part, 16)
        except ValueError:
            return False

    return True


async def _disconnect_device_async(device_address: str):
    """Helper function to disconnect device asynchronously."""
    device = device_manager.get_device(device_address)
    if device and device.is_connected:
        await device.disconnect()

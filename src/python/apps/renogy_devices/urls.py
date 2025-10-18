from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"renogy-devices", views.RenogyDeviceViewSet, basename="renogydevice")

urlpatterns = [
    path("", include(router.urls)),
    # Renogy device endpoints
    path("renogy/devices/", views.renogy_device_list, name="renogy_device_list"),
    path("renogy/devices/add/", views.renogy_device_add, name="renogy_device_add"),
    path(
        "renogy/devices/<str:device_address>/",
        views.renogy_device_remove,
        name="renogy_device_remove",
    ),
    path(
        "renogy/devices/<str:device_address>/connect/",
        views.renogy_device_connect,
        name="renogy_device_connect",
    ),
    path(
        "renogy/devices/<str:device_address>/disconnect/",
        views.renogy_device_disconnect,
        name="renogy_device_disconnect",
    ),
    path(
        "renogy/devices/<str:device_address>/data/",
        views.renogy_device_data,
        name="renogy_device_data",
    ),
    path(
        "renogy/devices/<str:device_address>/status/",
        views.renogy_device_status,
        name="renogy_device_status",
    ),
    path(
        "renogy/connect-all/",
        views.renogy_connect_all,
        name="renogy_connect_all",
    ),
    path(
        "renogy/disconnect-all/",
        views.renogy_disconnect_all,
        name="renogy_disconnect_all",
    ),
    path("renogy/all-data/", views.renogy_all_data, name="renogy_all_data"),
]

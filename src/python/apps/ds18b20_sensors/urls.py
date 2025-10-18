from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    r"ds18b20-sensors", views.DS18B20SensorViewSet, basename="ds18b20sensor"
)

urlpatterns = [
    path("", include(router.urls)),
    # DS18B20 sensor endpoints
    path(
        "ds18b20/sensors/",
        views.ds18b20_sensor_list,
        name="ds18b20_sensor_list",
    ),
    path(
        "ds18b20/sensors/add/",
        views.ds18b20_sensor_add,
        name="ds18b20_sensor_add",
    ),
    path(
        "ds18b20/sensors/<str:sensor_id>/",
        views.ds18b20_sensor_remove,
        name="ds18b20_sensor_remove",
    ),
    path(
        "ds18b20/sensors/<str:sensor_id>/temperature/",
        views.ds18b20_sensor_temperature,
        name="ds18b20_sensor_temperature",
    ),
    path(
        "ds18b20/sensors/<str:sensor_id>/info/",
        views.ds18b20_sensor_info,
        name="ds18b20_sensor_info",
    ),
    path(
        "ds18b20/discover/",
        views.ds18b20_discover_sensors,
        name="ds18b20_discover_sensors",
    ),
    path(
        "ds18b20/all-temperatures/",
        views.ds18b20_all_temperatures,
        name="ds18b20_all_temperatures",
    ),
    path(
        "ds18b20/summary/",
        views.ds18b20_sensor_summary,
        name="ds18b20_sensor_summary",
    ),
]

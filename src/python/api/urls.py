from django.urls import include, path

from apps.common.views.documentation import (
    api_changelog,
    api_examples,
    api_info,
    api_status,
)
from apps.ds18b20_sensors.urls import urlpatterns as ds18b20_sensors_urls
from apps.renogy_devices.urls import urlpatterns as renogy_devices_urls

urlpatterns = [
    # Renogy Devices App
    path("", include(renogy_devices_urls)),
    # DS18B20 Sensors App
    path("", include(ds18b20_sensors_urls)),
    # Documentation endpoints
    path("info/", api_info, name="api_info"),
    path("examples/", api_examples, name="api_examples"),
    path("status/", api_status, name="api_status"),
    path("changelog/", api_changelog, name="api_changelog"),
]

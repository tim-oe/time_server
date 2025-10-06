from django.urls import path, include

# Import app URLs
from apps.time_management.urls import urlpatterns as time_management_urls
from apps.renogy_devices.urls import urlpatterns as renogy_devices_urls
from apps.ds18b20_sensors.urls import urlpatterns as ds18b20_sensors_urls
from apps.common.views.documentation import (
    api_info,
    api_examples,
    api_status,
    api_changelog,
)

urlpatterns = [
    # Time Management App
    path("", include(time_management_urls)),
    
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
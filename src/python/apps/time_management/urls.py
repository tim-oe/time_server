from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"time-entries", views.TimeEntryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("time/", views.current_time, name="current_time"),
    path("health/", views.health_check, name="health_check"),
]

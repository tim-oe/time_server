# Django REST Framework Documentation

## Table of Contents
1. [Adding REST Endpoints](#adding-rest-endpoints)
2. [ASGI vs WSGI](#asgi-vs-wsgi)
3. [Complete Examples](#complete-examples)
4. [Best Practices](#best-practices)

## Adding REST Endpoints

### Overview
Django REST Framework (DRF) provides powerful tools for building REST APIs. This guide covers different approaches to creating endpoints, from simple function-based views to advanced class-based views with serializers.

### 1. Function-Based Views (FBV)

Function-based views are simple and straightforward for basic endpoints.

#### Basic Example
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def simple_endpoint(request):
    """Simple GET endpoint."""
    return Response({
        'message': 'Hello World',
        'method': request.method
    })

@api_view(['GET', 'POST'])
def flexible_endpoint(request):
    """Endpoint that handles both GET and POST."""
    if request.method == 'GET':
        return Response({'data': 'GET request received'})
    elif request.method == 'POST':
        return Response({'data': 'POST request received'}, status=status.HTTP_201_CREATED)
```

#### Advanced Function-Based View
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_timezone(request):
    """Get user's timezone information."""
    user = request.user
    return Response({
        'user': user.username,
        'timezone': str(timezone.get_current_timezone()),
        'current_time': timezone.now().isoformat(),
        'timestamp': timezone.now().timestamp()
    })
```

### 2. Class-Based Views (CBV)

Class-based views provide more structure and reusability.

#### APIView Example
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

class TimeAPIView(APIView):
    """Class-based view for time operations."""
    
    def get(self, request):
        """Handle GET requests."""
        return Response({
            'current_time': timezone.now().isoformat(),
            'timezone': str(timezone.get_current_timezone()),
            'unix_timestamp': timezone.now().timestamp()
        })
    
    def post(self, request):
        """Handle POST requests."""
        # Process time-related data
        data = request.data
        return Response({
            'message': 'Time data processed',
            'received_data': data
        }, status=status.HTTP_201_CREATED)
```

#### Generic Views Example
```python
from rest_framework import generics
from rest_framework.response import Response
from django.utils import timezone

class TimeListCreateView(generics.ListCreateAPIView):
    """Generic view for listing and creating time entries."""
    
    def list(self, request):
        """List time entries."""
        return Response({
            'times': [
                {
                    'id': 1,
                    'timestamp': timezone.now().isoformat(),
                    'description': 'Current time'
                }
            ]
        })
    
    def create(self, request):
        """Create a new time entry."""
        return Response({
            'message': 'Time entry created',
            'data': request.data
        }, status=status.HTTP_201_CREATED)
```

### 3. ViewSets

ViewSets provide the most powerful and flexible approach for complex APIs.

#### ModelViewSet Example
```python
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

class TimeViewSet(viewsets.ModelViewSet):
    """ViewSet for time-related operations."""
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current time."""
        return Response({
            'current_time': timezone.now().isoformat(),
            'timezone': str(timezone.get_current_timezone())
        })
    
    @action(detail=False, methods=['post'])
    def calculate_difference(self, request):
        """Calculate time difference."""
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        # Add your time calculation logic here
        return Response({
            'start_time': start_time,
            'end_time': end_time,
            'difference': 'calculated_difference'
        })
```

### 4. Serializers

Serializers handle data validation and transformation.

#### Basic Serializer
```python
from rest_framework import serializers
from django.utils import timezone

class TimeEntrySerializer(serializers.Serializer):
    """Serializer for time entries."""
    timestamp = serializers.DateTimeField()
    description = serializers.CharField(max_length=200)
    timezone = serializers.CharField(max_length=50)
    
    def validate_timestamp(self, value):
        """Validate timestamp."""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future")
        return value

class TimeEntryCreateSerializer(serializers.Serializer):
    """Serializer for creating time entries."""
    description = serializers.CharField(max_length=200)
    timezone = serializers.CharField(max_length=50, default='UTC')
```

#### Using Serializers in Views
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

class TimeEntryView(APIView):
    """View using serializers for validation."""
    
    def post(self, request):
        """Create a new time entry."""
        serializer = TimeEntryCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create time entry
            time_entry = {
                'timestamp': timezone.now(),
                'description': serializer.validated_data['description'],
                'timezone': serializer.validated_data['timezone']
            }
            
            return Response(time_entry, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

## ASGI vs WSGI

### What are ASGI and WSGI?

**WSGI (Web Server Gateway Interface)** and **ASGI (Asynchronous Server Gateway Interface)** are Python web server interfaces that define how web servers communicate with Python web applications.

### WSGI (Web Server Gateway Interface)

#### Purpose
- **Synchronous**: Handles one request at a time per worker
- **HTTP/1.1**: Designed for traditional HTTP requests
- **Mature**: Well-established standard since 2003
- **Simple**: Straightforward request-response cycle

#### Characteristics
```python
# WSGI Application Structure
def wsgi_application(environ, start_response):
    """WSGI application function."""
    # Process request synchronously
    response_body = process_request(environ)
    
    # Send response
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    
    return [response_body.encode()]
```

#### Use Cases
- Traditional web applications
- Simple REST APIs
- Applications without real-time features
- Legacy systems

#### Deployment
```bash
# Using Gunicorn (WSGI server)
gunicorn time_server.wsgi:application --bind 0.0.0.0:8000

# Using uWSGI
uwsgi --module time_server.wsgi:application --http :8000
```

### ASGI (Asynchronous Server Gateway Interface)

#### Purpose
- **Asynchronous**: Can handle multiple requests concurrently
- **HTTP/2 & WebSockets**: Supports modern web protocols
- **Real-time**: Enables WebSocket connections
- **Future-proof**: Designed for modern web applications

#### Characteristics
```python
# ASGI Application Structure
async def asgi_application(scope, receive, send):
    """ASGI application function."""
    if scope['type'] == 'http':
        # Handle HTTP request
        await handle_http_request(scope, receive, send)
    elif scope['type'] == 'websocket':
        # Handle WebSocket connection
        await handle_websocket(scope, receive, send)
```

#### Use Cases
- Real-time applications (chat, notifications)
- WebSocket connections
- HTTP/2 support
- High-concurrency applications
- Modern web APIs

#### Deployment
```bash
# Using Uvicorn (ASGI server)
uvicorn time_server.asgi:application --host 0.0.0.0 --port 8000

# Using Daphne
daphne -b 0.0.0.0 -p 8000 time_server.asgi:application
```

### When to Use Each

#### Use WSGI when:
- Building traditional REST APIs
- Simple web applications
- Legacy system integration
- Limited concurrency requirements
- Team familiar with synchronous programming

#### Use ASGI when:
- Need WebSocket support
- Building real-time features
- High concurrency requirements
- Modern web application architecture
- Want HTTP/2 support

### Configuration in Django

#### WSGI Configuration (wsgi.py)
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time_server.settings')
application = get_wsgi_application()
```

#### ASGI Configuration (asgi.py)
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time_server.settings')
application = get_asgi_application()
```

#### Enhanced ASGI with WebSocket Support
```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time_server.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})
```

## Complete Examples

### Example 1: Time Management API

Let's create a comprehensive time management API with multiple endpoints.

#### Models
```python
# api/models.py
from django.db import models
from django.utils import timezone

class TimeEntry(models.Model):
    """Model for storing time entries."""
    description = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.description} - {self.start_time}"
```

#### Serializers
```python
# api/serializers.py
from rest_framework import serializers
from .models import TimeEntry
from django.utils import timezone

class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimeEntry model."""
    
    class Meta:
        model = TimeEntry
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_start_time(self, value):
        """Validate start time."""
        if value > timezone.now():
            raise serializers.ValidationError("Start time cannot be in the future")
        return value
    
    def validate(self, data):
        """Validate the entire data set."""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")
        
        return data

class TimeEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating time entries."""
    
    class Meta:
        model = TimeEntry
        fields = ['description', 'start_time', 'end_time']
```

#### Views
```python
# api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from .models import TimeEntry
from .serializers import TimeEntrySerializer, TimeEntryCreateSerializer

class TimeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for time entries."""
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TimeEntryCreateSerializer
        return TimeEntrySerializer
    
    @action(detail=False, methods=['get'])
    def current_time(self, request):
        """Get current server time."""
        return Response({
            'current_time': timezone.now().isoformat(),
            'timezone': str(timezone.get_current_timezone()),
            'unix_timestamp': timezone.now().timestamp()
        })
    
    @action(detail=False, methods=['get'])
    def total_duration(self, request):
        """Get total duration of all time entries."""
        total = TimeEntry.objects.aggregate(
            total_duration=Sum('duration')
        )['total_duration']
        
        return Response({
            'total_duration': str(total) if total else '0:00:00',
            'total_seconds': total.total_seconds() if total else 0
        })
    
    @action(detail=True, methods=['post'])
    def stop_timer(self, request, pk=None):
        """Stop a running timer."""
        time_entry = self.get_object()
        
        if time_entry.end_time:
            return Response(
                {'error': 'Timer already stopped'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        time_entry.end_time = timezone.now()
        time_entry.duration = time_entry.end_time - time_entry.start_time
        time_entry.save()
        
        serializer = self.get_serializer(time_entry)
        return Response(serializer.data)
```

#### URLs
```python
# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'time-entries', views.TimeEntryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('time/', views.current_time, name='current_time'),
    path('health/', views.health_check, name='health_check'),
]
```

### Example 2: Authentication and Permissions

#### Views with Authentication
```python
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User

class UserTimeView(APIView):
    """View requiring authentication."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user-specific time data."""
        user = request.user
        return Response({
            'user': user.username,
            'email': user.email,
            'current_time': timezone.now().isoformat(),
            'timezone': str(timezone.get_current_timezone())
        })

class PublicTimeView(APIView):
    """Public view with read-only permissions."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        """Get public time information."""
        return Response({
            'current_time': timezone.now().isoformat(),
            'timezone': str(timezone.get_current_timezone()),
            'authenticated': request.user.is_authenticated
        })
```

## Best Practices

### 1. URL Design
```python
# Good URL patterns
urlpatterns = [
    path('api/v1/time-entries/', TimeEntryViewSet.as_view({'get': 'list'})),
    path('api/v1/time-entries/<int:pk>/', TimeEntryViewSet.as_view({'get': 'retrieve'})),
    path('api/v1/time-entries/<int:pk>/stop/', TimeEntryViewSet.as_view({'post': 'stop_timer'})),
]
```

### 2. Error Handling
```python
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """Custom exception handler."""
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': {
                'status_code': response.status_code,
                'message': response.data,
                'timestamp': timezone.now().isoformat()
            }
        }
        response.data = custom_response_data
    
    return response
```

### 3. Pagination
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
    'MAX_PAGE_SIZE': 100
}
```

### 4. Filtering and Search
```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class TimeEntryViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['start_time', 'end_time']
    search_fields = ['description']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-created_at']
```

### 5. Testing
```python
# api/tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone

class TimeEntryAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_time_entry(self):
        """Test creating a time entry."""
        data = {
            'description': 'Test time entry',
            'start_time': timezone.now().isoformat()
        }
        response = self.client.post('/api/time-entries/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_current_time(self):
        """Test getting current time."""
        response = self.client.get('/api/time/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('current_time', response.data)
```

This documentation provides a comprehensive guide to building REST APIs with Django REST Framework, covering everything from basic endpoints to advanced patterns, along with detailed explanations of ASGI and WSGI functionality.

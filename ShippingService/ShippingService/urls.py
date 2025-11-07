from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from shippingapp.views import ShippingViewSet, health_check, get_shipment_detail

# Router setup
router = routers.DefaultRouter()
router.register(r'shipping', ShippingViewSet, basename='shipping')

# Swagger API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Shipping Service API",
        default_version='v1',
        description="API for managing and tracking shipments",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('v1/', include(router.urls)),
    path('v1/health/', health_check, name='health-check'),
    path('v1/shipping/<int:pk>/detail/', get_shipment_detail, name='shipment-detail'),

    # Swagger documentation only
    path('ship-doc/', schema_view.with_ui('swagger', cache_timeout=0), name='ship-doc'),
]

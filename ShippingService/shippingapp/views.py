from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from django.db import connection

from .models import Shipment
from .serializers import ShipmentSerializer
from .Service.order_client import get_order_details, update_order_shipping_status
from .Status.order_status import OrderStatus
from .Status.shipping_status import ShippingStatus
from .Service.inventory_client import update_inventory
from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError

def health_check(request):
    """Basic liveness probe — app is up."""
    return JsonResponse({"status": "ok"}, status=200)

def readiness_check(request):
    """Readiness probe — checks DB connectivity."""
    db_conn = connections['default']
    try:
        db_conn.cursor()
        return JsonResponse({"status": "ready"}, status=200)
    except OperationalError:
        return JsonResponse({"status": "not ready"}, status=503)

class ShippingViewSet(viewsets.GenericViewSet):
    """
    Handles shipment creation and updates,
    while synchronizing with the Order Service.
    """
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer

    # -------------------- CREATE SHIPMENT --------------------
    @swagger_auto_schema(
    operation_summary="Create a new shipment",
    operation_description=(
        "Creates a shipment for an order that is CONFIRMED.\n\n"
        f"**Allowed Order Status:** {', '.join([s.value for s in OrderStatus])}\n"
        f"**Shipping Status Options:** {', '.join([s.value for s in ShippingStatus])}"
    ),
    request_body=ShipmentSerializer,
    responses={201: ShipmentSerializer, 400: "Invalid or failed operation"},
    )
    @action(detail=False, methods=['post'], url_path='create')
    def create_shipment(self, request):
        """Create shipment for confirmed orders and sync with Order Service."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data.get("order_id")

        # Verify order exists and is confirmed
        order = get_order_details(order_id)
        if not order:
            return Response(
                {"error": "Order not found or unavailable"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.get("order_status") != OrderStatus.CONFIRMED.value:
            return Response(
                {"error": f"Shipment allowed only for {OrderStatus.CONFIRMED.value} orders"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create shipment (initially PENDING)
        shipment = serializer.save(status=ShippingStatus.PENDING.value)

        # Notify Order Service → mark as SHIPPED
        if not update_order_shipping_status(order_id, ShippingStatus.SHIPPED.value):
            shipment.delete()
            return Response(
                {"error": "Failed to update order service"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update local shipment status
        shipment.status = ShippingStatus.SHIPPED.value
        shipment.save()

        # Update inventory for each item from the order
        items = order.get("items", [])
        if not items:
            return Response(
                {"error": "No items found in order for inventory update"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for item in items:
            item_id = item.get("item_id")
            quantity = item.get("quantity")
            if not item_id or quantity is None:
                continue
            update_inventory(item_id=item_id, quantity_change=quantity)

        return Response(
            ShipmentSerializer(shipment).data,
            status=status.HTTP_201_CREATED,
        )


    # -------------------- UPDATE SHIPMENT STATUS --------------------
    @swagger_auto_schema(
        operation_summary="Update shipment status",
        operation_description=(
            f"Updates shipment (Allowed: {', '.join([s.value for s in ShippingStatus])}) "
            "and syncs the new status with Order Service."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[s.value for s in ShippingStatus],
                    description="New shipping status"
                )
            },
            required=['status']
        ),
        responses={201: ShipmentSerializer, 400: "Invalid update"},
    )
    @action(detail=True, methods=['patch'], url_path='update')
    def update_status(self, request, pk=None):
        """Update shipment status and sync with Order Service."""
        shipment = self.get_object()
        new_status = request.data.get("status")

        if not new_status or new_status not in [s.value for s in ShippingStatus]:
            return Response({"error": "Invalid shipping status"}, status=status.HTTP_400_BAD_REQUEST)

        shipment.status = new_status
        shipment.save()

        if not update_order_shipping_status(shipment.order_id, new_status):
            return Response({"error": "Failed to sync with Order Service"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)



# -------------------- GET SHIPMENT DETAILS --------------------
@swagger_auto_schema(
    method='get',
    operation_summary="Get shipment details",
    operation_description="Retrieve shipment info by ID.",
    responses={200: ShipmentSerializer, 404: "Not found"},
)
@api_view(['GET'])
def get_shipment_detail(request, pk=None):
    """Retrieve details of a specific shipment by ID."""
    try:
        shipment = Shipment.objects.get(pk=pk)
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_200_OK)
    except Shipment.DoesNotExist:
        return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)


# -------------------- HEALTH CHECK --------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Check database and service connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
        return JsonResponse({"status": "healthy"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=500)

from django.http import HttpResponse

def metrics(request):
    """
    Basic Prometheus-compatible metrics endpoint.
    """
    content = (
        "# HELP shipping_service_health_status 1 if healthy, else 0\n"
        "# TYPE shipping_service_health_status gauge\n"
        "shipping_service_health_status 1\n"
    )
    return HttpResponse(content, content_type="text/plain")


from django.db import models
from django.utils import timezone
from .Status.shipping_status import ShippingStatus

class Shipment(models.Model):
    shipment_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    carrier = models.CharField(max_length=100)
    tracking_no = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[(status.value, status.value) for status in ShippingStatus],
        default=ShippingStatus.PENDING.value
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment {self.tracking_no} - {self.status}"

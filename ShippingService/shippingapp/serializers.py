from rest_framework import serializers
from .models import Shipment
from .Status.shipping_status import ShippingStatus

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = '__all__'

    def validate_status(self, value):
        """Ensure the status value is one of the valid enum options."""
        valid_statuses = [status.value for status in ShippingStatus]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status '{value}'. Must be one of {valid_statuses}."
            )
        return value

    def validate(self, data):
        """Check logical timestamp consistency."""
        shipped_at = data.get('shipped_at')
        delivered_at = data.get('delivered_at')
        status = data.get('status')

        # Validate logical order of events
        if delivered_at and not shipped_at:
            raise serializers.ValidationError(
                "Cannot set delivered_at without shipped_at."
            )

        # Auto rules for consistency between status and timestamps
        if status == ShippingStatus.DELIVERED.value and not delivered_at:
            raise serializers.ValidationError(
                "Delivered status requires delivered_at timestamp."
            )
        if status == ShippingStatus.SHIPPED.value and not shipped_at:
            raise serializers.ValidationError(
                "Shipped status requires shipped_at timestamp."
            )

        return data

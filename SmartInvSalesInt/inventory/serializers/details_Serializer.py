from rest_framework import serializers
from inventory.models import InventoryMovement
from rest_framework.exceptions import PermissionDenied


class InfoProductPrivateSerializer(serializers.ModelSerializer):

    

    class Meta:
        model = InventoryMovement
        fields = [
            "product",
            "quantity",
            "old_stock",
            "new_stock",
            "movement_type",
            "reason",
            "created_by",
            "created_at",
        ]

        read_only_fields = fields

    def to_representation(self, instance):
        request = self.context.get("request")

        if not request:
            return super().to_representation(instance)
            

        user = request.user
        role = user.userprofile.role

        if role not in ["owner", "manager", "supervisor"]:
            
            raise PermissionDenied(
            "Not allowed to you."
        )

        return super().to_representation(instance)


from rest_framework import serializers
from inventory.models import InventoryMovement

class ProductStockAdjustmentSerializer(serializers.ModelSerializer):
    
    product_name = serializers.CharField(
        source = "product.product_name", 
        read_only = True
    )

    class Meta:
        model = InventoryMovement

        fields = [
            'product',
            "product_name",
            'quantity',
            'movement_type',
            'reason',
            
        ]

    def validate_quantity(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be grater than zero."
            )
        
        return value
    
    def validate(self, data):

        product = data.get("product")
        quantity = data.get("quantity")
        movement_type = data.get("movement_type")

        # Insure inventory exists
        if not hasattr(product, "inventory"):

            raise serializers.ValidationError(
                "Inventory record not found for this product."
            )
        
        inventory = product.inventory

        # Prevent stock going negative.
        if movement_type =="OUT":

            if quantity > inventory.quantity:

                raise serializers.ValidationError(
                    "Insufficient stock avaiable."
                )
        return data

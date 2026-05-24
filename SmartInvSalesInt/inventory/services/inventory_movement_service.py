from django.db import transaction
# from products.models import ProductModel

from rest_framework.exceptions import(
    PermissionDenied,
    ValidationError
)

from inventory.models import(
    InventoryMovement, 
    Inventory
)


class InventoryUpdateService:

    ALLOWED_ROLES = (
        "owner",
        "manager",
        "supervisor",
    )

    @staticmethod
    @transaction.atomic
    def create_update_inventory(
        product, 
        quantity, 
        movement_type, 
        user, 
        reason = None
    ):

        profile = user.userprofile

        if profile.role not in (
            InventoryUpdateService.ALLOWED_ROLES
        ):
            
            raise PermissionDenied(
                "you are not allowed to make changes."
            )
        
        if product.company != profile.company:
            raise PermissionError(
                "You cannot access the product."
            )
        
        if product.is_deleted:
            raise ValidationError(
                "Product is deleted."
            )
        
        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than  Zero."
            )
        
        inventory, _ = Inventory.objects.select_for_update().get_or_create(
            product = product
        )

        if profile.role not in ["owner", "manager", "supervisor"]:
            raise PermissionError(
                "You are not allow to make changes."
            )
        
        
        old_stock = inventory.quantity

        if movement_type == "IN":

            new_stock = old_stock + quantity

        elif movement_type == "OUT":

            if quantity > old_stock:

                raise ValueError(
                    "Insufficient stock."
                )
            
            new_stock = old_stock - quantity
        
        elif movement_type == "ADJ":

            if not reason:

                raise ValueError(
                    "Reason is required for adjustment."
                )
            
            new_stock = quantity
        
        else:

            raise ValueError(
                "Invalid movement type."
            )

        inventory.quantity = new_stock

        inventory.save()

        # Creating movement logs
        movement = InventoryMovement.objects.create(
            product = product,
            quantity = quantity,
            movement_type = movement_type,
            old_stock = old_stock,
            new_stock = new_stock,
            reason = reason,
            created_by = user,
        )
        return movement





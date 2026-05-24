from django.db import transaction
from products.models import ProductModel
from inventory.models import InventoryMovement
from django.utils import timezone

class ProductServices:

    @staticmethod
    def _validate_product_data(data):

        cost  = data.get("cost_price")
        selling  = data.get("selling_price")

        if cost is None or cost < 0:
            raise PermissionError("Cost price must be positve")

        if selling is None or selling < 0:
            raise PermissionError("Selling price must be positve")
        
        if selling < cost:
            raise ValueError(
                "Selling price cannot be less than cost price"
            )
        # margin logic (10%)
        miniunm_selling = cost * 1.10
        
        if selling < miniunm_selling:
            raise ValueError(
                f"Margin should be 10 percent at list. Selling price should be more that {cost}. "
            )
        return cost, selling
    
    @staticmethod
    def _check_permission(user):
        role = user.userprofile.role
        if role in ["worker"]:
            raise PermissionError("You are not allowed to create product")

    @staticmethod
    def _generate_sku(data):
        """
        Basic SKU generator
        """
        base = data.get("product_name").upper().replace(" ","")[:5]
        timestamp = int(timezone.now().timestamp())
        return f"{base}-{timestamp}"
    
    
    @staticmethod
    @transaction.atomic
    def create_product(data, user):

        # permission check
        ProductServices._check_permission(user)

        # Validation check
        cost, selling = ProductServices._validate_product_data(data)

        # Generated SKU
        sku = data.get("sku") or ProductServices._generate_sku(data)

        stock = data.get("stock_quantity", 0)
        company = user.userprofile.company


        # Product creation
        product = ProductModel.objects.create(
            product_name = data.get("product_name"),
            sku = sku, # Note: make a different function for it to give unique Id.
            created_by = user,
            company = company,
            cost_price = cost,
            selling_price = selling,
            supplier_name = data.get("supplier_name"),
            stock_quantity = stock,
            category = data.get("category"),
            created_at = timezone.now(),
            is_active = True
        )
        
        if stock > 0:

            InventoryMovement.objects.create(
                product = product,
                quentity = stock,
                new_stock = stock,
                movement_type = "IN",
                reason = "Opening Stock",
                create_at = timezone.now()
            )

        return product
    
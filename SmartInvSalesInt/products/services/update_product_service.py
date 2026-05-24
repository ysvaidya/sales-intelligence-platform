
"""
    Issues
    1 cost price should not be updated
    2 sku can be but no.
    3 stock quantity.

"""
from django.db import transaction


class ProductUpdateService:

    # Permission Logic

    @staticmethod
    def _check_permission(user, product):
        profile = user.userprofile

        if profile.role in ["worker"]:
            raise PermissionError("You are not allow to make changes.")

        if product.company != profile.company:
            raise PermissionError("You cannot access the product.")

        if product.is_deleted:
            raise ValueError("You cannot Updated the product values.")


    # Validation Logic
    @staticmethod
    def _validate_pricing(data, product):

        if "cost_price" in data:
            raise ValueError("Cost price cannot be updated.")
        
        if "sku" in data:
            raise ValueError("SKU can not be change.")

        cost = product.cost_price
        selling = data.get("selling_price", product.selling_price)

        if selling is not None and selling < 0:
            raise ValueError(
                "Selling price can not be negative."
            )
        
        if cost is not None and cost < 0:
            raise ValueError(
                "Cost price cannot be negative."
            )
        
        if selling < cost:
            raise ValueError(
                "Selling price cannot be lower than cost price."
            )
        
        minimum_selling = cost * 1.10


        if selling < minimum_selling:
            raise ValueError(
                f"Minimum selling price for 10% margin is {minimum_selling}."
            )
        return selling


    # Field Update
    @staticmethod
    def _apply_updates(product, data, selling):

        update_fields = []

        if "product_name" in data:
            value = data.get("product_name").strip()
            if not value:
                raise ValueError("Product name cannot be empty.")
            product.product_name = value
            update_fields.append("product_name")

        if "supplier_name" in data:
            value = data.get("supplier_name").strip()
            if not value:
                raise ValueError("Supplier name cannot be empty.")
            product.supplier_name = value
            update_fields.append("supplier_name")
        
        
        if "selling_price" in data:
            product.selling_price = selling
            update_fields.append("selling_price")
        
        if "category" in data:
            product.category = data.get("category")
            update_fields.append("category")

        return update_fields
    

    @classmethod
    @transaction.atomic
    def update_product( cls, data, product, user):

        # step 1: Permission
        cls._check_permission(user, product)

        #step 2: Validation
        selling = cls._validate_pricing(data, product)

        #step 3: Apply updates
        updated_fields = cls._apply_updates(product, data, selling)

        # step 4: Save
        
        if updated_fields:
            product.save(updated_fields = updated_fields)

        return product
    

        

        

        
        
        
        
    

# class movementInvUpdateService:

from django.db import models
from products.models import ProductModel
from django.contrib.auth.models import User


# Create your models here.

class Inventory(models.Model):

    
    product = models.OneToOneField(
        ProductModel,
        on_delete=models.CASCADE,
        related_name = "inventory")
    
    quantity = models.PositiveIntegerField(
        default = 0,
        help_text = "Available stock quantity"
    )

    updated_at = models.DateTimeField(
        auto_now = True
    )

    created_at = models.DateTimeField(
        auto_now_add = True
    )

    class Meta:
        ordering = ["product__product_name"]

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"



class InventoryMovement(models.Model):

    class MovementType(models.TextChoices):
        STOCK_IN = "IN", "Stock In"
        STOCK_OUT = "OUT", "Stock Out"
        ADJUSTMENT = "ADJ", "Adjustment"

    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.PROTECT,
        related_name = "stock_movements"
    )

    old_stock = models.PositiveIntegerField(
        default = 0,
        help_text = "Stock quantity before movement."
    )

    quantity = models.PositiveIntegerField(
        help_text = "Quantity changed during movement."
    )
    
    new_stock = models.PositiveIntegerField(
        default = 0,
        help_text = "Optional explanation fro stack change."
    )

    movement_type = models.CharField(
        max_length=3,
        choices = MovementType.choices,
        db_index = True
    )

    reason = models.TextField(
        ("Reason"), 
        blank = True,
        help_text="Optional explanation for stock change."
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        related_name = "inventory_movements",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index = True
    )

    class Meta:
        ordering = ["-created_by"]
        verbose_name = "Inventory Movement"
        verbose_name_plural = "Inventory Movements"

    def __str__(self):
        return (
            f"{self.product.product_name} | "
            f"{self.movement_type} | "
            f"{self.quantity}"
        )

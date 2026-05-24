from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Company

# Create your models here.

class Categories(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete = models.CASCADE,
        related_name= "categories"
    )

    name = models.CharField(max_length=100) 

    class Meta:
        unique_together = ["sku", "company"] # when both are combined the unique ness is increased.
        # indexes = [
        #     models.Index(fields=["company","product_name"]),
        # ]

    def __str__(self):
        return self.name

class ProductModel(models.Model):

    product_name = models.CharField( 
        max_length=100,
    )

    created_by = models.ForeignKey( 
        User,
        on_delete=models.SET_NULL,
        null = True,
        related_name="product_created",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name = "products",
    )

    sku = models.CharField( 
        max_length=50,
        db_index=True, # Faster search when selling product by SKU
    )

    cost_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators = [MinValueValidator(0)], # more than Zero
        help_text= "Actual Price of the product."
    )

    selling_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators = [MinValueValidator(0)], # more than Zero
        help_text= "Selling Price of the product."
    )

    supplier_name = models.CharField( 
        max_length=50,
    )

    category = models.ForeignKey(
         Categories,
        on_delete=models.PROTECT,
        related_name="products",
    )

    is_active = models.BooleanField( default = True)

    created_at = models.DateTimeField(
        # default = timezone.now
        auto_now_add = True
    )

    updated_at = models.DateTimeField( auto_now=True )

    deleted_at = models.DateTimeField(
        null = True, 
        blank = True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "sku"],
                name = "unique_company_sku"
            )
        ]

        indexes = [
            models.Index(
                fields=["company", "product_name"]
            )
        ]

        ordering = ["-created_at"]

        
    def clean(self):
        if self.selling_price < self.cost_price:
            raise ValidationError(
                {
                    "selling_price": "Selling price must be greater than or equal to actual price."
                }
            )
    
    def delete(self, *args, **kwargs):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at"])
    
    def __str__(self):
        return f"{self.product_name} ({self.sku})"




from rest_framework import serializers
from products.models import ProductModel

class ProductListSerializer(serializers.ModelSerializer):
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if request and hasattr(request.user, "userprofile"):
        # user = self.context['request'].user
            role = request.user.userprofile.role

            restricted_fields_by_role = {
                "worker": ["created_by"],
            }

            restricted_fields = restricted_fields_by_role.get(role, [])

            if restricted_fields:
                data = {
                    key : value

                    for key, value in data.items()
                    if key not in restricted_fields
                }

        return data
    
    class Meta:
        model = ProductModel
        fields  = [
            "id",
            "product_name",
            "created_by",
            "selling_price",
            "stock_quantity",
            "category",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if request and hasattr(request.user, "userprofile"):
            role = request.user.userprofile.role

            restricted_fields_by_role = {
                "worker" :[
                    "crated_by",
                    "cost_price",
                    "sku",
                    "category",
                    "crated_at",
                    "updated_at",

                ]
            }
            restricted_fields = restricted_fields_by_role.get(role, [])

            if restricted_fields:
                data = {
                    key: value
                    for key, value in data.items()
                    if key not in restricted_fields
                }
        return data

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "product_name",
            "created_by",
            "cost_price",
            "sku",
            "selling_price",
            "supplier_name",
            "stock_quantity",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "sku",
            "created_at",
            "updated_at",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):

    class Meta:

        model = ProductModel
        fields = [
            "id",
            "product_name",
            "sku",
            "cost_price",
            "selling_price",
            "supplier_name",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
        
    def validate_product_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Product Name cannot be Empty."
            )
        return value
    
    def validate_supplier_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Supplier Name cannot be Empty."
            )
        return value
    
    def validate_cost_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost price cannot be negative")
        return value

    def validate_selling_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Selling price cannot be negative")
        return value
    
    def validate(self, data):

        cost = data.get("cost_price")
        selling = data.get("selling_price")

        if cost is not None and selling is not None:
            if selling < cost:
                raise serializers.ValidationError(
                    "Selling price cannot be lower than cost price."
                ) 
            
        return data
    
    def create(self, validated_data):
        request = self.context.get("requests")
        user = request.user

        validated_data["created_by" ] = user
        validated_data["company"] = user.userprofile.company

        return super().create(validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "product_name",
            "created_by",
            "sku",
            "cost_price",
            "selling_price",
            "supplier_name",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "sku",
            "created_at",
            "updated_at",
            "is_active",
        ]
    
    # Reusable def
    def _validate_non_empty(self, value, field_name):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                f"{field_name} cannot be empty"
            )
        return value
    
    def _validate_pricing(self,value, field_name):
        if value < 0:
            raise serializers.ValidationError(
                f"{field_name} cannot be empty or negative"
            )
        return value

    def validate_product_name(self, value):
        return self._validate_non_empty(value, "Product Name")
    
    def validate_supplier_name(self, value):
        return self._validate_non_empty(value, "Supplier Name")
    
    def validate_cost_price(self, value):
        return self._validate_pricing(value, "Cost Price")


    def validate_selling_price(self, value):
        return self._validate_pricing(value, "Selling Price")
    
    def validate(self, data):
        
        """
        Ensure selling_price is not lower than cost_price.
        Must handle PATCH correctly.
        """
        instance = getattr(self, "instance",None)

    # Use new value if provided, otherwise fallback to existing value
        cost = data.get("cost_price", getattr(instance, "cost_price", None ))
    # Same goes to selling.
        selling = data.get("selling_price", getattr(instance, "selling_price", None))

        if cost is not None and selling is not None:
            if selling < cost:
                raise serializers.ValidationError(
                    "Selling price cannot be lover than cost price."
                ) 
            
        return data

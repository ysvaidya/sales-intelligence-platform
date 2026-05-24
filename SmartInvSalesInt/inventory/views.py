from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle

from rest_framework.exceptions import ValidationError

from django.shortcuts import get_object_or_404

from .models import InventoryMovement
from products.models import ProductModel

from inventory.serializers.create_serializer import ProductStockAdjustmentSerializer
from inventory.serializers.details_Serializer import InfoProductPrivateSerializer

from inventory.services.inventory_movement_service import InventoryUpdateService

from inventory.permissions.inventory_permission import InvenotoryAccessPermission

from .pagination import InventoryPagination

# Create your views here.

class InventoryMovementUpdate(APIView):

    permission_classes = [
        IsAuthenticated,
        InvenotoryAccessPermission
    ] 
    
    throttle_classes = [UserRateThrottle]

    def post(self, request, pk):

        product = get_object_or_404(
            ProductModel,
            pk = pk,
            is_deleted = False
        )

        serializer = (
            ProductStockAdjustmentSerializer(
                data = request.data,
                context = {"request": request}
            )
        )

        serializer.is_valid(raise_exception = True)

        quantity = serializer.validated_data["quantity"]

        movement_type = serializer.validated_data["movement_type"]
        
        reason = serializer.validated_data.get("reason")
        

        InventoryUpdateService.create_update_inventory(
            product = product,
            quantity = quantity,
            movement_type = movement_type,
            user = request.user,
            reason = reason
        )

        return Response(
            {
                "Message" : "Inventory Updated Successfully."
            },
            status = status.HTTP_200_OK
        )


class InvertoryWatchList(ListAPIView):

    permission_classes = [
        IsAuthenticated,
        InvenotoryAccessPermission
    ]

    throttle_classes = [UserRateThrottle]

    serializer_class = (
        InfoProductPrivateSerializer
    )

    pagination_class = InventoryPagination

    filter_backends = [
        SearchFilter, 
        OrderingFilter
    ]

    search_fields = [
        "product__product_name",
        "movement_type",
        "reason",
        "created_by__username"
    ]

    ordering_fields = [
        "created_by",
        "product__product_name",
        "new_stock",
        "old_stock",
        "quentity",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        
        product_id = self.kwargs.get("pk")
        
        product = get_object_or_404(
            ProductModel, 
            pk = product_id, 
            created_by = self.request.user,
            is_deleted = False
        )
        
        queryset = InventoryMovement.objects.filter(
            product = product,
        )
        
        movement_type = (
            self.request.query_params.get("type")
        )

        allowed_types = ["IN", "OUT", "ADJ"]

        if (
            movement_type and movement_type not in allowed_types
        ):
            raise ValidationError(
                "Invalid movement type"
            )

        if movement_type:
            queryset = queryset.filter(
                movement_type = movement_type
            )

        return queryset



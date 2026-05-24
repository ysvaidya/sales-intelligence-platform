from django.shortcuts import render

# Apis import files 
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView, 
    RetrieveAPIView, 
    CreateAPIView
)
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.throttling import UserRateThrottle

from django.core.exceptions import ValidationError

import logging

logger = logging.getLogger(__name__)

from serializers.product import (
    ProductListSerializer,
    ProductDetailSerializer, 
    ProductCreateSerializer, 
    ProductUpdateSerializer
) 

from products.services.create_product_service import ProductServices
from products.services.update_product_service import ProductUpdateService
from products.services.status_service import ProductStatusService
from products.services.delete_service import RemoveProductService

from .models import ProductModel

from .pagination import ProductPagination


# --------------
# Basic View
# --------------

def index (request):
    return render(request, "index.html")

# --------------
# Reusable Company Mizin
# --------------

class CompanyProductMixin:
    def get_company_products(self):
        return ProductModel.object.filter(
            company = self.request.user.userprofile.company
        )
    
# --------------
# Product Create View
# --------------

class ProductCreateView(CreateAPIView):

    permission_classes = [IsAuthenticated] 
    throttle_classes = [UserRateThrottle]

    serializer_class = ProductCreateSerializer

    def post(self, request):

        serializer = ProductCreateSerializer(
            data = request.data,
            context = {"request": request}
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

        try:
            product = ProductServices.create_product(
                serializer.validated_data,
                request.user
            )


        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status = status.HTTP_400_BAD_REQUEST
            )
        
        except PermissionError as e:
            return Response(
                {"error" : 'Not allowed.'}, 
                status = status.HTTP_403_FORBIDDEN
            )
        
        response_serializer = ProductDetailSerializer(
            product,
            context = {"request": request}
        )
        
        return Response(
            response_serializer.data, 
            status = status.HTTP_201_CREATED
        ) 

# --------------
# Product List View
# --------------

class ProductListView(
    CompanyProductMixin,
    ListAPIView
    
):
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    serializer_class = ProductListSerializer
    pagination_class = ProductPagination

    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        "product_name",
        "created_by__username",
        "supplier_name",
        "category__name",                
    ]

    ordering_fields = [
        "created_at", 
        "product_name"
    ]

    ordering = ["-created_at"] # default 

    def get_queryset(self):
        
        return self.get_company_products().filter(
            is_active = True, 
            is_deleted = False,
        )
        
# --------------
# Product Detail View
# --------------
    
class ProductDetailView(
    CompanyProductMixin,
    RetrieveAPIView
):

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        # product_id = self.kwargs.get("pk")
        
        return self.get_company_product().filter(
            # pk = product_id,
            is_active = True,
            is_deleted = False
        )
        
# ------------------------------------------------------
# Product Update View
# ------------------------------------------------------

class ProductUpdateView(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def patch(self, request, pk):

        try:
            product = ProductModel.objects.select_for_update().get(
                pk=pk, 
                created_at = request.user, 
                is_active=True
            ) # Error Here.

        except ProductModel.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductUpdateSerializer(
            product,
            data  = request.data,
            partial = True,
            contex = {"request": request}
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_product = ProductUpdateService.update_product(
                serializer.validated_data,
                product, 
                request.user
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)}, 
                status = status.HTTP_400_BAD_REQUEST
            )
        except PermissionError:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_SEE_OTHER
            )
        response_serializer = ProductDetailSerializer(
            updated_product,
            context = {"request": request})
        
        return Response(
            response_serializer.data,
            status = status.HTTP_202_ACCEPTED
        )
    

# ------------------------------------------------------
# Product Update View
# ------------------------------------------------------

class ProductSoftDeleteView(APIView):
    
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def delete(self, request, pk):

        try:
            product = ProductModel.objects.filter(
                pk = pk, 
                created_at = request.user, 
                is_active = True
            )

        except ProductModel.DoesNotExist:
            return Response(
                {"error":"Product not Found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            RemoveProductService.soft_delete_product(
                product,
                request.user,
            )

        except ValidationError as e: 
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except PermissionError:
            return Response(
                {"error": "Not allowed."},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {"message" : "Product deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import (
    UserRateThrottle, 
    AnonRateThrottle
)
from rest_framework import status
from django.core.exceptions import ValidationError
from rest_framework.exceptions import (
    ValidationError, 
    PermissionDenied
)

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User

from SmartInvSalesInt.accounts.serializers.owner_serializer import (
    OwnerRegisterSerializer
)

from SmartInvSalesInt.accounts.serializers.employee_serializer import (
    EmployeeCreatioSerializer, 
    EmployeeUpdateSerializer
) 
from SmartInvSalesInt.accounts.serializers.employee_list_serializer import (
    EmployeeListSerializer
)

from accounts.services import AccountServices
from .permissions import IsManagerOrAbove


# --------------------------
# Owner Registertion
# --------------------------

class OwnerAccountView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):

        serializer = OwnerRegisterSerializer(
            data = request.data,
            context ={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data

        try:

            owner = AccountServices.register_owner(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                company_name=data["company_name"],
                
            )

        except (
            ValidationError, 
            PermissionDenied, 
            ValueError
        ) as e:
            return Response(
                {"error": str(e)}, 
                status = status.HTTP_400_BAD_REQUEST
            )
        

        except Exception as e:
            
            return Response(
                {"error": "Something went wrong"},
                status = status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        refresh = RefreshToken.for_user(owner)
        profile = owner.userprofile

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": owner.username,
                "company": profile.company.name,
                "role": profile.role,
            },
            status=status.HTTP_201_CREATED
        )
# -------------------
# Employee Creation
# -------------------
    
class EmployeeAccountView(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):

        serializer = EmployeeCreatioSerializer(
            data = request.data, 
            context = {"request": request}
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST 
            )
        
        data = serializer.validated_data

        try:

            emp_user = AccountServices.create_employee(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=data["role"],
                creator_user=request.user
            )

        except(
            PermissionDenied, 
            ValidationError, 
            ValueError
        ) as e:

            return Response(
                {"error" : str(e)},
                status = status.HTTP_403_FORBIDDEN
            )
        
        except Exception as e:
            return Response(
                {"error" : "Something went wrong"},
                status = status.HTTP_500_INTERNAL_SERVER_ERROR  
            )
        
        profile  = emp_user.userprofile
        
        return Response(
            {
                "message": 
                "Employee created successfully",

                "employee": {
                    "username": 
                    emp_user.username,

                    "role": 
                    profile.role,

                    "company": 
                    profile.company.name,
                }
            },
            status=status.HTTP_201_CREATED
        )
# -----------------
# Employee list
# -----------------

class EmployeeListView(APIView):

    permission_classes = [
        IsAuthenticated, 
        IsManagerOrAbove
    ]

    throttle_classes = [
        UserRateThrottle
    ]

    def get(self, request):

        company = request.user.userprofile.company

        employees = (
            User.objects.filter(
            userprofile__company = company
            ).select_related(
                "userprofile", 
                "userprofile__company"
            )
        )

        serializer = EmployeeListSerializer(
            employees, 
            many = True
        )

        return Response(
            serializer.data, 
            status = status.HTTP_200_OK
        )
    

# -----------------------
# Employee Update
# -----------------------

class EmployeeUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsManagerOrAbove
    ]

    throttle_classes = [
        UserRateThrottle
    ]

    def patch(self, request,user_id):

        employee = get_object_or_404(
            User.objects.select_related(
                "userprofile",
                "userprofile__company"
            ),
            id = user_id
        )

        serializer = EmployeeUpdateSerializer(
            instance = employee,
            data = request.data,
            partial = True,
            context = {"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data

        try:

            update_user = (
                AccountServices.update_employee(
                    employee_user = employee,
                    updater_user = request.user,
                    email = data.get("email"),
                    role = data.get("role")
                )
            )
        
        except(
            PermissionDenied,
            ValidationError,
            ValueError
        ) as e:
            
            return Response(
                {"error": "Someting went wrong"},
                status = status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        profile = update_user.userprofile

        return Response(
            {
                "message":
                "Employee updated sucessfully",

                "employee":{
                    "username":
                    update_user.username,

                    "email":
                    update_user.email,

                    "role":
                    profile.role,

                    "company":
                    profile.company.name,

                }
            },
            status = status.HTTP_200_OK
        )
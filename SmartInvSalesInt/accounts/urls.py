from django.urls import path
from .views import (
    OwnerAccountView,
    EmployeeAccountView,
    EmployeeListView,
    EmployeeUpdateView
)

urlpatterns = [

    path(
        "owner/register/",
        OwnerAccountView.as_view(),
        name="owner-register"
    ),

    path(
        "employee/create/",
        EmployeeAccountView.as_view(),
        name="employee-create"
    ),

    path(
        "employees/",
        EmployeeListView.as_view(),
        name="employee-list"
    ),

    path(
        "employees/<int:user_id>/update/",
        EmployeeUpdateView.as_view(),
        name="employee-update"
    ),
]
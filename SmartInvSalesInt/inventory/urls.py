
from django.urls import path

from inventory.views import (
    InventoryMovementUpdate,
    InvertoryWatchList,
)

urlpatterns = [

    path(
        "update/<int:pk>/",
        InventoryMovementUpdate.as_view(),
        name="inventory-update"
    ),

    path(
        "history/<int:pk>/",
        InvertoryWatchList.as_view(),
        name="inventory-history"
    ),
]
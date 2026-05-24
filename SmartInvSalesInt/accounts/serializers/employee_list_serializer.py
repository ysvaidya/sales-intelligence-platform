from rest_framework import serializers
from django.contrib.auth.models import User

class EmployeeListSerializer (serializers.ModelSerializer):
    role = serializers.ReadOnlyField(
        source = "userprofile.role"
    )

    company = serializers.ReadOnlyField(
        source = "userprofile.company.name"
    )

    class Meta:
        model = User
        fields = [
            "id", 
            "username", 
            "email", 
            "role", 
            "company"
        ]

        read_only_fields = fields
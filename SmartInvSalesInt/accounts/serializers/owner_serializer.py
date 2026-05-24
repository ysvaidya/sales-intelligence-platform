from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from accounts.models import Company

class OwnerRegisterSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length = 100,
        trim_whitespace = True,
    )

    email = serializers.EmailField(
        max_length = 100,
        trim_whitespace = True,
    )
    
    password = serializers.CharField(
        write_only = True,
        trim_whitespace = False,
        style = {"input_type": "password"}
    )

    company_name = serializers.CharField(
        max_length = 100,
        trim_whitespace = True
    )

    def validate_username(self,value):
        value = value.strip().lower()

        if User.objects.filter(
            username = value
        ).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value
    
    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(
            email=value
        ).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )
        
        return value

    def validate_password(self, value):
        validate_password(value)
        return value
    
    def validate_company_name(self, value):
        value = value.strip()

        if Company.objects.filter(
            name = value
        ).exists():
            raise serializers.ValidationError(
                "Company already exists."
            )
        
        return value
from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from models import UserProfile

from accounts.models import UserProfile

class EmployeeCreatioSerializer(serializers.Serializer):
    
    username = serializers.CharField(
        max_length = 100,
        trim_whitespace = True,
    )

    email = serializers.EmailField(
        trim_whitespace = True,
        max_length = 100,
    )
    
    password = serializers.CharField(
        write_only = True,
        trim_whitespace = False,
        style = {"input_type": "password"}
    )

    role = serializers.ChoiceField(
        choices = [
            UserProfile.Role.MANAGER,
            UserProfile.Role.SUPERVISOR,
            UserProfile.Role.WORKER,
        ]
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
    
    def validate(self, attrs):

        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError(
                "Request context required."
            )
        
        current_user_role = request.user.userprofile.role
        target_role = attrs["role"]


        if current_user_role == "worker":
            raise serializers.ValidationError(
                "You are not allowed to create employees."
            )
        
        if (
            current_user_role == "superviser" 
            and target_role == "manager"
        ):
            raise serializers.ValidationError(
                "Superviser cannot create manager."
            )
        
        return attrs


class EmployeeUpdateSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=False,
        trim_whitespace=True,
        max_length=254
    )

    role = serializers.ChoiceField(
        required=False,
        choices=[
            UserProfile.Role.MANAGER,
            UserProfile.Role.SUPERVISOR,
            UserProfile.Role.WORKER,
        ]
    )

    def validate_email(self, value):
        value = value.strip().lower()

        user = self.instance

        if (
            User.objects
            .filter(email=value)
            .exclude(id=user.id)
            .exists()
        ):
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate(self, attrs):

        request = self.context.get("request")

        if not request:
            raise serializers.ValidationError(
                "Request required."
            )

        requester_role = request.user.userprofile.role

        target_role = attrs.get("role")

        if target_role:

            if requester_role == "worker":
                raise serializers.ValidationError(
                    "Worker cannot update employees."
                )

            if (
                requester_role == "supervisor"
                and target_role == "manager"
            ):
                raise serializers.ValidationError(
                    "Supervisor cannot assign manager role."
                )

        return attrs

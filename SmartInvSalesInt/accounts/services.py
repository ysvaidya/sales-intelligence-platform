from django.contrib.auth.models import User
from django.db import transaction
from .models import Company, UserProfile

class AccountServices:

    @staticmethod
    @transaction.atomic
    def register_owner(
        username, 
        email, 
        password, 
        company_name
    ):

        user = User.objects.create_user(
            username=username,
            email=email,
            password = password
        )

        company = Company.objects.create(
            name=company_name,
            owner = user,
        )

        UserProfile.objects.create(
            user = user,
            company = company,
            role = "owner"
        )

        return user
    
    @staticmethod
    @transaction.atomic
    def create_employee(
        username, 
        email, 
        password, 
        role, 
        creator_user
    ):

        profile = creator_user.userprofile 
        creator_role = profile.role
        company = profile.company

        valid_roles = [
            UserProfile.Role.MANAGER,
            UserProfile.Role.SUPERVISOR,
            UserProfile.Role.WORKER,
        ]

        if role not in valid_roles:
            raise ValueError(
                "Invalid role"
            )

        if creator_role == UserProfile.Role.OWNER:
            pass

        elif creator_role == UserProfile.Role.MANAGER:
            raise PermissionError(
                "Manager cannot create another manager"
            )

        elif creator_role in [
            UserProfile.Role.SUPERVISOR,
            UserProfile.Role.WORKER
        ]:
            raise PermissionError(
                "You are not allow to create users."
            )
        
        user = User(
            username = username,
            email = email,
            password = password,
        )

        UserProfile.objects.create(
            user = user,
            company = company,
            role = role
        )

        return user
    
    @staticmethod
    @transaction.atomic

    def update_employee(
        employee_user,
        updater_user,
        email = None,
        role = None
    ):
        
        updater_profile = updater_user.userprofile
        employee_profile = employee_user.userprofile

        updater_role = updater_profile.role

        if (
            updater_profile.company
            != employee_profile.company
        ):
            raise PermissionError(
                "Different company."
            )
        
        if updater_role == UserProfile.Role.WORKER:
            raise PermissionError(
                "Worker cannot update employee."
            )
        
        if (
            updater_role == UserProfile.Role.SUPERVISOR
            and role == UserProfile.Role.MANAGER
        ):
            raise PermissionError(
                "supervisor cannot assign manager."
            )
        
        if email:
            employee_user.email = email

        if role:
            employee_profile.role = role

            employee_user.save()


        

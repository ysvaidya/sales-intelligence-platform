from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Company(models.Model):
    name = models.CharField( 
        max_length=100, 
        unique=True,
        db_index=True,
    )

    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="owned_companies"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(
        default=True,
        db_index= True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    
class Permission(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.CharField(
        max_length=100, 
        unique=True,
        db_index=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(models.Model):

    class Role(models.TextChoices):

        OWNER = 'owner','OWNER'
        MANAGER = 'manager','MANAGER'
        SUPERVISOR = 'supervisor', 'SUPERVISOR'
        WORKER = 'worker','WORKER'
    

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name = "userprofile"
    )
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name = "users"
    )
    
    role = models.CharField(
        max_length=50,
        choices = Role.choices, 
        default = Role.WORKER,
        db_index=True
    )

    permissions = models.ManyToManyField(
        Permission,
        blank = True,
        related_name = "users",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "company"],
                name = "unique_user_company"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - ({self.role}) - {self.company.name}"
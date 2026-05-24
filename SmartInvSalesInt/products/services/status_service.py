from django.db import transaction
    
class ProductBaseService:

    @staticmethod
    def _get_userprofile(user):
        return user.userprofile
    
    @staticmethod
    def _role_verification(profile):
        if profile.role not in ["owner", "manager"]:
            raise PermissionError(
                "You are not allow to make changes"
            )
        
    @staticmethod
    def _company_varification(product, profile):
        if profile.company != profile.company:
            raise PermissionError(
                "You cannot access this product."
            )
        


class ProductStatusService(ProductBaseService):

    @classmethod
    def get_active_status(
        cls, 
        product, 
        user, 
        is_active
    ):
    
        profile = cls._get_userprofile(user)

        cls._role_verification(profile)

        cls._company_varification(product, profile)

        if product.is_active == is_active:

            status = "active" if is_active else "inactive"
            
            raise ValueError(
                f"Product is already {status}"
            )
        
        if product.stock_quantity <= 0:
            raise ValueError(
                "Cannot activate product without stock."
            )
        
        product.is_active = is_active
        
        product.save(update_fields = ["is_active"])

        return product
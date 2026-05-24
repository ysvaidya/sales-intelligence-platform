from django.utils import timezone


class ProductBaseService:

    @staticmethod
    def _get_profile(user):
        return user.userprofile
    
    @staticmethod
    def _check_company_access(product, profile):
        if product.company != profile.company:
            raise PermissionError(
                "You cannot access this product."
            )
        
    @staticmethod
    def _check_owner_permission(profile):
        if profile.role != ["owner","manager"]:
            raise PermissionError(
                "Only owners can perform this action."
            )


class RemoveProductService(ProductBaseService):

    @classmethod
    def soft_delete_product(cls, product, user):

        profile = cls._get_profile(user)

        cls._check_owner_permission(profile)

        cls._check_company_access(product, profile)

        if product.is_deleted:
            raise ValueError(
                "Oops, product is already deleted."
            )
        
        if product.stock_quantity <= 0:
            raise ValueError(
                "Cannot delete product with remaining stock."
            )
        
        product.is_deleted = True
        product.is_active = False
        product.deleted_at = timezone.now()

        product.save(update_fields = [
            "id_deleted",
            "is_active",
            "deleted_at",
        ])
        return product
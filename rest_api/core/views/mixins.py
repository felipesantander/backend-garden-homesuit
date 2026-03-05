from django.db.models import Q
from core.models import UserRole

class BusinessFilterMixin:
    """
    Mixin to filter querysets based on the businesses allowed in the user's role permissions.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        if user.is_superuser:
            return queryset

        # Get the active role. We follow the logic in CustomTokenObtainPairSerializer:
        # standard is taking the first role assigned to the user.
        user_role = user.user_roles.first()
        if not user_role:
            return queryset.none()

        role = user_role.role
        allowed_businesses = set()
        has_full_access = False

        for permission in role.permissions.all():
            if "*" in permission.businesses:
                has_full_access = True
                break
            allowed_businesses.update(permission.businesses)

        if has_full_access:
            return queryset

        if not allowed_businesses:
            return queryset.none()

        model_name = self.queryset.model.__name__
        
        if model_name == "Garden":
            return queryset.filter(business_id__in=allowed_businesses)
        elif model_name == "Machine":
            return queryset.filter(garden__business_id__in=allowed_businesses)
        elif model_name == "Channel":
            return queryset.filter(business_id__in=allowed_businesses)

        return queryset

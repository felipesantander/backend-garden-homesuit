from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["id_usuario"] = user.id
        token["username"] = user.username

        # Get role and components
        user_role = user.user_roles.first()
        if user_role:
            role = user_role.role
            token["role"] = role.name
            
            # Gather all components from all permissions of the role
            components = set()
            for permission in role.permissions.all():
                if permission.components:
                    components.update(permission.components)
            
            token["components"] = list(components)
        else:
            token["role"] = None
            token["components"] = []

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra response data if needed
        data["user_id"] = self.user.id
        data["role"] = self.user.user_roles.first().role.name if self.user.user_roles.exists() else None
        
        return data

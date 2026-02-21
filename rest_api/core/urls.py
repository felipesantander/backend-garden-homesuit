from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from core.views.auth.token import CustomTokenObtainPairView
from core.views.Business.views import BusinessViewSet
from core.views.Channel.views import ChannelViewSet
from core.views.ConfigurationChannel.views import ConfigurationChannelViewSet
from core.views.Data.views import DataViewSet, ingest_data
from core.views.Garden.views import GardenViewSet
from core.views.Machine.views import MachineViewSet
from core.views.MachineCandidate.views import MachineCandidateViewSet
from core.views.Notification.views import NotificationViewSet
from core.views.Permission.views import PermissionViewSet
from core.views.Role.views import RoleViewSet
from core.views.UserRole.views import UserRoleViewSet

router = DefaultRouter()
router.register(r"machines", MachineViewSet)
router.register(r"channels", ChannelViewSet)
router.register(r"data", DataViewSet)
router.register(r"businesses", BusinessViewSet)
router.register(r"gardens", GardenViewSet)
router.register(r"notifications", NotificationViewSet)
router.register(r"permissions", PermissionViewSet)
router.register(r"roles", RoleViewSet)
router.register(r"user-roles", UserRoleViewSet)
router.register(r"configuration-channels", ConfigurationChannelViewSet)
router.register(r"machine-candidates", MachineCandidateViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("ingest/", ingest_data, name="ingest_data"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

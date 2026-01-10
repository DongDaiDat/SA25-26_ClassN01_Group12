from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from modules.shared.permissions import role_permission
from .serializers import UserSerializer, CreateUserSerializer

User = get_user_model()

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

class LogoutViewSet(viewsets.ViewSet):
    def create(self, request):
        # blacklist refresh token
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"error": {"code":"MISSING_REFRESH","message":"refresh is required","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=400)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({"error": {"code":"INVALID_REFRESH","message":"invalid refresh token","details":{}, "trace_id": getattr(request,"request_id",None)}}, status=400)
        return Response({}, status=204)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("username")
    filterset_fields = ["role","is_active"]
    search_fields = ["username","email","first_name","last_name"]
    ordering_fields = ["username","date_joined"]

    def get_permissions(self):
        if self.action in ("list","retrieve","create","update","partial_update","destroy"):
            return [role_permission("ADMIN")()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def whoami(request):
    u = request.user
    return Response({"id": str(u.id), "username": u.username, "email": u.email, "role": u.role})

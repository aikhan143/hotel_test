from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.generics import CreateAPIView
from .serializers import *
from .models import *

class PermissionMixin:
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class RoomViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomImageView(CreateAPIView):
    queryset = RoomImage.objects.all()
    serializer_class = RoomImageSerializer
    permission_classes = [IsAdminUser]
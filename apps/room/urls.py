from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register('rooms', RoomViewSet)

urlpatterns = [
    path('rooms/add-room-image/', RoomImageView.as_view()),
    path('', include(router.urls))
]
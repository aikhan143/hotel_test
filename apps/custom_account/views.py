from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsActive

from .serializers import *

class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response('Вы успешно зарегистрировались', status=201)

class ActivateView(APIView):
    def get(self, request, email, activation_code):
        user = User.objects.filter(email=email, activation_code=activation_code).first()
        if not user:
            return Response('Пользователь не найден', 400)
        user.activation_code = ''
        user.is_active = True
        user.save()
        return Response('Activated', 200)
    
class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response('Вам был отправлен код на почту. Пожалуйста, проверьте.', status=201)
    
class ForgotPasswordCompleteView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordCompleteSerializer)
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordCompleteSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response('Вы успешно сменили пароль', status=201)
    
class ChangePasswordView(APIView):
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        data = request.data
        serializer = ChangePasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response('Вы успешно сменили пароль', status=201)

class UserView(APIView):
    serializer_class = AccountSerializer
    permission_classes = IsActive,

    def get_queryset(self):
        return User.objects.get(email=self.request.user)

    def get(self, request, *args, **kwargs):
        user = self.get_queryset()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=200)

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = User.objects.get(email=self.request.user)
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)

        if request.data.get('email'):
            return Response('Нельзя менять почтовый адрес', status=400)

        instance = self.get_queryset()
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)

    def delete(self, request, *args, **kwargs):
        user_instance = self.request.user
        instance = User.objects.get(email=user_instance)
        instance.delete()
        return Response('Вы успешно удалили аккаунт', status=204)
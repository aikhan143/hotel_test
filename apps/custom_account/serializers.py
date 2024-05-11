from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from .tasks import send_activation_code, send_verification_email

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    password_confirm = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'image', 'phone_number', 'password', 'password_confirm']

    def validate_email(self, email):
        try:
            User.objects.get(email=email)
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        except:
            return email

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        phone_number = attrs['phone_number'].strip()

        if not password == password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        
        if not password.isalnum():
            raise serializers.ValidationError('Пароль не должен содержать символов')
        
        if phone_number[0] != '+':
            attrs['phone_number'] = '+' + phone_number

        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        send_activation_code.delay(user.email, user.activation_code)
        return user
    
class ForgotPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email']

    def validate_email(self, email):
        if User.objects.get(email=email):
            return email
        raise serializers.ValidationError ('Пользователь не существует')
    
    def send_verification_email(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        send_verification_email.delay(user.email, user.activation_code)

class ForgotPasswordCompleteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    password_confirm = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'activation_code']

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('activation_code')
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if not User.objects.filter(email=email, activation_code=code).exists() and password == password_confirm:
            raise serializers.ValidationError('Неверный пароль или код')
        
        if not password.isalnum():
            raise serializers.ValidationError('Пароль не должен содержать символов')
        return attrs
    
    def create_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.activation_code = ''
        user.save()

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(min_length=8, required=True, write_only=True)
    new_password = serializers.CharField(min_length=8, required=True, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = ['email']

    def validate_email(self, email):
        if User.objects.get(email=email):
            return email
        raise serializers.ValidationError ('Пользователь не существует')
    
    def validate_old_password(self, old_password):
        user = self.context.get('request').user
        if user.check_password(old_password):
            return old_password
        raise serializers.ValidationError ('Неверный пароль')
    
    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        
        if new_password == old_password:
            raise serializers.ValidationError('Старый и новый пароль не может быть похожим')
        
        if not new_password.isalnum():
            raise serializers.ValidationError('Пароль не должен содержать символов')
        
        return attrs
    
    def create_new_password(self):
        new_password = self.validated_data.get('new_password')
        user = self.context.get('request').user
        user.set_password(new_password)
        user.save()

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    # def validate(self, attrs):
    #     phone_number = attrs['phone_number']
    #     if phone_number[0] != '+':
    #         attrs['phone_number'] = '+' + phone_number

    #     return attrs

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        data = {
            'first_name': f"{repr['first_name']}",
            'last_name': f"{repr['last_name']}",
            'email': repr['email'],
            'phone_number': repr['phone_number'],
        }
        return data
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.utils.crypto import get_random_string

class UserManager(BaseUserManager):
    def _create(self, email, password=None,first_name=None, last_name=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен для ввода')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password, first_name, last_name, **extra):
        extra.setdefault('is_staff', False)
        return self._create(email, password, first_name, last_name, **extra)
        
    def create_superuser(self, email, password, first_name=None, last_name=None, **extra):
        extra.setdefault('is_active', True)
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self._create(email, password, first_name, last_name, **extra)

class User(AbstractUser):
    last_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=15, blank=True)
    image = models.ImageField(upload_to='account_img/', blank=True, null=True, verbose_name='Аватарка')
    phone_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    
    objects = UserManager()

    username = None
    groups = None
    user_permissions = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def create_activation_code(self):
        code = get_random_string(10)
        self.activation_code = code
        self.save()
        return code
    
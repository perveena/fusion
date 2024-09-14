from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=128, null=False)
    profile = models.JSONField(default=dict, null=False)
    status = models.IntegerField(default=0, null=False)
    settings = models.JSONField(default=dict, null=True)
    created_at = models.BigIntegerField(null=True, blank=True)
    updated_at = models.BigIntegerField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = int(timezone.now().timestamp() * 1000)
        self.updated_at = int(timezone.now().timestamp() * 1000)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email

class Organization(models.Model):
    name = models.CharField(max_length=255, null=False)
    status = models.IntegerField(default=0, null=False)
    personal = models.BooleanField(default=False, null=True)
    settings = models.JSONField(default=dict, null=True)
    created_at = models.BigIntegerField(null=True, blank=True)
    updated_at = models.BigIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically set timestamps
        if not self.created_at:
            self.created_at = int(timezone.now().timestamp() * 1000)
        self.updated_at = int(timezone.now().timestamp() * 1000)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Role(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    
class Member(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, null=False)
    settings = models.JSONField(default=dict, null=True)
    created_at = models.BigIntegerField(null=True, blank=True)
    updated_at = models.BigIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = int(timezone.now().timestamp() * 1000)
        self.updated_at = int(timezone.now().timestamp() * 1000)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} in {self.org.name}"


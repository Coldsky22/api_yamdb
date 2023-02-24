from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class UserManagerYaMDB(UserManager):
    def create_superuser(self, username, email=None,
                         password=None, **extra_fields):
        extra_fields.setdefault('role', UserRole.ADMIN)
        return super().create_superuser(username, email,
                                        password, **extra_fields)


class User(AbstractUser):
    objects = UserManagerYaMDB()
    last_name = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        null=True,
    )
    role = models.CharField(
        max_length=9,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='E-mail',
    )
    confirmation_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Код подтверждения',
    )

    password = models.CharField(blank=True, null=True, max_length=128)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (
            self.role == UserRole.ADMIN
            or self.is_staff
            or self.is_superuser
        )

    @property
    def is_moder(self):
        return self.role == UserRole.MODERATOR

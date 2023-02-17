from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
# Create your models here.


class Role(models.TextChoices):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moder'


class UserManagerApiYAMBD(UserManager):
    def create_superuser(self, username, email=None,
                         password=None, **extra_fields):
        extra_fields.setdefault('role', Role.ADMIN)
        return super().create_superuser(username,
                                        email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManagerApiYAMBD()
    bio = models.TextField(verbose_name='Биография пользователя',
                           blank=True,)
    role = models.CharField(max_length=10,
                            choices=Role.choices,
                            default=Role.USER,
                            verbose_name='Роль пользователя',)

    email = models.EmailField(
        max_length=160, unique=True, verbose_name='Почта')
    confirmation_code = models.CharField(max_length=25, blank=True,
                                         verbose_name='Код подтвердения',)

    @property
    def is_admin(self):
        return (self.role == Role.ADMIN or self.is_staff or self.is_superuser)

    @property
    def is_moder(self):
        return self.role == Role.MODERATOR

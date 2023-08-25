from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from rest_framework.exceptions import ValidationError


REGEX_VALIDATOR = RegexValidator(
    regex=r'^(?!foodgram$)(?!me$)(?!$)[\w.@+-]+\Z(?! +$)')


class User(AbstractUser):

    username = models.CharField(
        db_index=True, max_length=150, unique=True, blank=False, null=False,
        verbose_name='Имя пользователя', validators=[REGEX_VALIDATOR, ]
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False, null=False,
    )

    first_name = models.CharField(
        max_length=150, blank=False, verbose_name='Имя', null=False,)
    last_name = models.CharField(
        max_length=150, blank=False, verbose_name='Фамилия', null=False,)
    password = models.CharField(max_length=150, blank=False,
                                verbose_name='Пароль', null=False,
                                unique=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-username', )

    def __str__(self):
        return self.username

    def clean(self):
        if not self.username.strip():
            raise ValidationError("Username cannot be empty.")


class UsersFollowing(models.Model):
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Инфлюенсер'
    )
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_follow = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(fields=['following', 'follower'],
                                    name='unique_follow'),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f"Подписчик: '{self.follower}', Инфлюенсер: '{self.following}'"

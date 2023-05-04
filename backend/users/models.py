from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Псевдоним'
    )
    first_name = models.CharField(
        max_length=30,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=128,
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'author'],
                name='subscriber_author'
            ),
        ]

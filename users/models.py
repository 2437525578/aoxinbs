from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone  # 对应 datetime


class CustomUser(AbstractUser):
    # Django 的 AbstractUser 已经包含了 username, email, password (hash)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),  # Flask models.py 中 role 默认值是 staff
        ('user', 'User'),  # Flask user_routes.py 注册时默认值是 user
    )

    # 覆盖 email 字段使其唯一 (Flask 模型中是唯一的)
    email = models.EmailField(unique=True, blank=False, null=False)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    def __str__(self):
        return self.username

    # 确保 createsuperuser 创建的用户角色为 admin
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)
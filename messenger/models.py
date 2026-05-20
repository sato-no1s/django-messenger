from django.db import models

from user.models import CustomUser

# Create your models here.
class Group(models.Model):
    name = models.CharField(
        verbose_name='名前',
        max_length=100,
    )
    created_at = models.DateTimeField(
        verbose_name='新規登録日時',
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        verbose_name='更新日時',
        auto_now=True
    )
    
    def __str__(self):
        return self.name

class GroupUser(models.Model):
    group = models.ForeignKey(
        Group,
        verbose_name='グループ',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name='ユーザ',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        verbose_name='新規登録日時',
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        verbose_name='更新日時',
        auto_now=True
    )
    
    def __str__(self):
        return self.id

class Message(models.Model):
    body = models.TextField(
        verbose_name='本文',
    )
    group = models.ForeignKey(
        Group,
        verbose_name = 'グループ',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        CustomUser,
        verbose_name='ユーザ',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        verbose_name='新規登録日時',
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        verbose_name='更新日時',
        auto_now=True
    )
    
    def __str__(self):
        return self.id
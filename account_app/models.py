import time
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import re

class MyUserManager(BaseUserManager):
    def create_user(self, email, created_at, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            created_at=created_at,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,created_at, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            created_at=created_at,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=40,
        unique=True,
    )
    username = models.CharField(
        max_length=40,
        primary_key=True
    )
    created_at = models.DateField()
    role = models.ForeignKey('Role',on_delete=models.SET_NULL,null=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['created_at']

    def __str__(self):
        return self.email


class Role(models.Model):
    role = models.CharField(max_length=40,primary_key=True)
    description = models.CharField(max_length=100)
    fun1 = models.BooleanField(default=False)
    fun2 = models.BooleanField(default=False)
    fun3 = models.BooleanField(default=False)
    fun4 = models.BooleanField(default=False)
    fun5 = models.BooleanField(default=False)
    fun6 = models.BooleanField(default=False)
    fun7 = models.BooleanField(default=False)
    fun8 = models.BooleanField(default=False)

class Contract(models.Model):
    contractnum = models.AutoField(primary_key=True)
    contractname = models.CharField(max_length=40)
    clientnum = models.ForeignKey('Client',on_delete=models.SET_NULL,null=True)
    begintime = models.DateField()
    endtime = models.DateField()
    content = models.CharField(max_length=200)
    draft = models.ForeignKey('MyUser',on_delete=models.SET_NULL,null=True)
    state = models.IntegerField(default=0,choices=((0,'待分配'),(1,'会签中'),(2,'定稿中'),(3,'审批中'),(4,'签订中'),(5,'签订完成')))
    file = models.FileField()
    uploadtime = models.DateField()

class Client(models.Model):
    clientnum = models.CharField(max_length=20,primary_key=True)
    clientname = models.CharField(max_length=40)
    address = models.CharField(max_length=100)
    tel = models.CharField(max_length=20)
    fax = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    bank = models.CharField(max_length=50)
    account = models.CharField(max_length=50)
    addition = models.CharField(max_length=100)
    username = models.ForeignKey('MyUser',on_delete=models.CASCADE)

class Administration(models.Model):
    contractnum = models.ForeignKey('Contract',on_delete=models.CASCADE)

    countersign1 = models.ForeignKey('MyUser',on_delete=models.SET_NULL,null=True,related_name='c1')
    option1 = models.CharField(max_length=100)
    ctime1 = models.DateTimeField()
    countersign2 = models.ForeignKey('MyUser', on_delete=models.SET_NULL, null=True,related_name='c2')
    option2 = models.CharField(max_length=100)
    ctime2 = models.DateTimeField()
    countersign3 = models.ForeignKey('MyUser', on_delete=models.SET_NULL, null=True,related_name='c3')
    option3 = models.CharField(max_length=100)
    ctime3 = models.DateTimeField()

    approval1 = models.ForeignKey('MyUser',on_delete=models.SET_NULL,null=True,related_name='a1')
    astate1 = models.IntegerField(default=0,choices=((0,'未审批'),(1,'拒绝'),(2,'通过')))
    atime1 = models.DateTimeField()
    approval2 = models.ForeignKey('MyUser', on_delete=models.SET_NULL, null=True,related_name='a2')
    astate2 = models.IntegerField(default=0, choices=((0, '未审批'), (1, '拒绝'), (2, '通过')))
    atime2 = models.DateTimeField()
    approval3 = models.ForeignKey('MyUser', on_delete=models.SET_NULL, null=True,related_name='a3')
    astate3 = models.IntegerField(default=0, choices=((0, '未审批'), (1, '拒绝'), (2, '通过')))
    atime3 = models.DateTimeField()

    sign = models.ForeignKey('MyUser',on_delete=models.SET_NULL,null=True)
    sinformation = models.CharField(max_length=100)
    stime = models.DateField()

class log(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.ForeignKey('MyUser', on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=200)
    time = models.DateTimeField()
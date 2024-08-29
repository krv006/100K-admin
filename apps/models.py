# import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

from django.db import models
from django.db.models import Model, DateTimeField, UUIDField, CharField, SlugField, ImageField, DecimalField, \
    ForeignKey, CASCADE, TextChoices, EmailField, TextField, BooleanField, IntegerField, SET_NULL, FloatField

from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field



class CreatedAtBase(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# class Base(CreatedAtBase):
#     # id = UUIDField(primary_key=True, db_default=RandomUUID(), editable=False) # postgres da ishlatiladi
#     id = UUIDField(default=uuid.uuid4, primary_key=True)  # sqlite uchun basic
#
#     class Meta:
#         abstract = True


class BaseSlugModel(CreatedAtBase):
    name = CharField(max_length=255)
    slug = SlugField(unique=True)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
        self.slug = slugify(self.name)
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug += '-1'
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        user = self.create_user(phone_number, password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractUser):
    class Role(TextChoices):
        ADMIN = "admin", 'Admin'
        OPERATOR = "operator", 'Operator'
        MANAGER = "manager", 'Manager'
        DRIVER = "driver", 'Driver'
        USER = "user", 'User'

    username = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    role = CharField(max_length=50, choices=Role.choices, default=Role.USER)
    phone_number = CharField(max_length=12, unique=True)
    district = ForeignKey('apps.District', CASCADE, related_name='users', null=True)
    image = ImageField(upload_to='users/')


class Category(BaseSlugModel):
    image = ImageField(upload_to='category-image/')


class Product(BaseSlugModel):
    name = CharField(max_length=255)
    price = models.FloatField()
    short_description = CKEditor5Field()
    long_description = CKEditor5Field()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')


class ImageProduct(Model):
    image = ImageField(upload_to='products/%Y/%m/%d/')
    video = models.FileField(upload_to='products/videos/%Y/%m/%d/', blank=True, null=True)
    product = ForeignKey('apps.Product', CASCADE, related_name='images')

    def __str__(self):
        return f"ImageProduct for {self.product}"


class Order(CreatedAtBase):
    class Region(TextChoices):
        ANDIJON = "andijon", "Andijon"
        BUXORO = "buxoro", "Buxoro"
        FARGONA = "fargona", "Farg'ona"
        JIZZAX = "jizzax", "Jizzax"
        XORAZM = "xorazm", "Xorazm"
        NAMANGAN = "namangan", "Namangan"
        NAVOIY = "navoiy", "Navoiy"
        QASHQADARYO = "qashqadaryo", "Qashqadaryo"
        QORAQALPOGISTON = "qoraqalpogiston", "Qoraqalpog'iston"
        SAMARQAND = "samarqand", "Samarqand"
        SIRDARYO = "sirdaryo", "Sirdaryo"
        SURXONDARYO = "surxondaryo", "Surxondaryo"
        TOSHKENT = "toshkent", "Toshkent"

    name = CharField(max_length=50)
    phone_number = CharField(max_length=50)
    region = CharField(max_length=255, choices=Region.choices)
    product = ForeignKey('apps.Product', CASCADE, to_field='slug', related_name='orders')


class Review(Model):
    name = CharField(max_length=255)
    email = EmailField(max_length=255, null=True, blank=True)
    description = TextField()
    comment_status = TextField()
    created_at = DateTimeField(auto_now_add=True)
    product = ForeignKey('apps.Product', CASCADE, related_name='reviw')

    def __str__(self):
        return self.name


class Region(Model):
    name = CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=255, unique=True)
    region = ForeignKey('apps.Region', CASCADE, related_name='districts')

    def __str__(self):
        return self.name


class Stream(CreatedAtBase):
    name = CharField(max_length=255)
    discount = FloatField()
    count = IntegerField(default=0)
    product = ForeignKey('apps.Product', SET_NULL, null=True, related_name='streams')
    user = ForeignKey('apps.User', CASCADE, related_name='streams')

    class Meta:
        ordering = '-id',

    def str(self):
        return self.name


class SiteSettings(Model):
    pass

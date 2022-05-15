from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class AdminDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Mobile = models.CharField(max_length=12)
    Image = models.ImageField(upload_to='images', blank=True)
    Address = models.CharField(max_length=250, blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to="images/")

    def _str_(self):
        return self.name

class UserDetails(models.Model):
    full_name = models.CharField(max_length=100,blank=True,null=True)
    username = models.CharField(max_length=100,unique=True)
    user_email = models.EmailField(unique=True)
    password = models.CharField(max_length=8)
    address = models.CharField(max_length=250,blank=True,null=True)
    mobile = models.CharField(max_length=12)
    image = models.ImageField(upload_to='images')

    def _str_(self):
        return self.username


class product(models.Model):
    Name = models.CharField(max_length=100)
    Brand = models.CharField(max_length=100)
    Category = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    per_unit = models.CharField(max_length=100)
    Qty = models.IntegerField()
    Rate = models.IntegerField()
    Discount = models.IntegerField()
    Percentage = models.IntegerField()
    Total_rate = models.IntegerField()
    Top_product = models.CharField(max_length=20)
    Image = models.ImageField(upload_to='images', blank=True, null=True)


class product_images(models.Model):
    Product = models.ForeignKey(product, on_delete=models.CASCADE, null=True)
    Image_path = models.ImageField(upload_to='images', blank=True, null=True)


class Offers(models.Model):
    image = models.ImageField(upload_to="images/")


class Cart(models.Model):
    User =  models.ForeignKey(UserDetails, on_delete=models.CASCADE, null=True)
    Product = models.ForeignKey(product, on_delete=models.CASCADE)
    Qty_count = models.IntegerField()
    Rate = models.IntegerField()
    Discount = models.IntegerField()
    Total_rate = models.IntegerField()


class My_order(models.Model):
    User = models.ForeignKey(UserDetails, on_delete=models.CASCADE, null=True)
    Product = models.ForeignKey(product, models.SET_NULL, blank=True, null=True)
    Product_name = models.CharField(max_length=200)
    Brand = models.CharField(max_length=200)
    Category = models.CharField(max_length=200)
    Qty_count = models.CharField(max_length=200)
    Rate = models.IntegerField()
    Discount = models.IntegerField()
    Total_rate = models.IntegerField()
    Status = models.CharField(max_length=100)
    Message = models.CharField(max_length=240)
    Booking_address = models.CharField(max_length=240)
    datetime = models.DateTimeField(auto_now=True)

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    balance = models.IntegerField(default=10000)


class Restaurant(models.Model):
    name = models.CharField()


class Dish(models.Model):
    name = models.CharField()
    price = models.FloatField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')


class ShoppingCart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    time = models.DateTimeField(auto_now_add=True)


class Position(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='positions')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()

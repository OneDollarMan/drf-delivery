from django.contrib import admin
from api.models import CustomUser, Dish, Order, Position, Restaurant, ShoppingCart

admin.site.register(CustomUser)
admin.site.register(Restaurant)
admin.site.register(Dish)
admin.site.register(ShoppingCart)
admin.site.register(Order)
admin.site.register(Position)


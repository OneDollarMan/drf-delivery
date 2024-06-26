from django.urls import path
from .views import AddToCartView, CheckoutView, OrderListView, RemoveFromCartView, RestaurantListView, ShoppingCartView

urlpatterns = [
    path('menu/', RestaurantListView.as_view(), name='menu'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/', ShoppingCartView.as_view(), name='view-cart'),
    path('cart/checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order-list'),
]


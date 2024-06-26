from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Restaurant, Dish, CustomUser, ShoppingCart, Order, Position
from datetime import timedelta
from django.utils import timezone


class CartOrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

        # Create a restaurant
        self.restaurant = Restaurant.objects.create(name='Test Restaurant')

        # Create dishes
        self.dish1 = Dish.objects.create(name='Dish 1', price=10.0, restaurant=self.restaurant)
        self.dish2 = Dish.objects.create(name='Dish 2', price=15.0, restaurant=self.restaurant)

    def test_add_to_cart(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Send a POST request to add a dish to the cart
        response = self.client.post('/api/cart/add/', {'dish_id': self.dish1.id, 'quantity': 2}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the dish is added to the cart
        self.assertEqual(ShoppingCart.objects.filter(user=self.user).count(), 1)

    def test_remove_from_cart(self):
        # Create a cart item
        cart_item = ShoppingCart.objects.create(user=self.user, dish=self.dish1, quantity=1)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Send a POST request to remove a dish from the cart
        response = self.client.post('/api/cart/remove/', {'dish_id': self.dish1.id, 'quantity': 1}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the dish is removed from the cart
        self.assertEqual(ShoppingCart.objects.filter(user=self.user).count(), 0)

    def test_view_cart(self):
        # Create cart items
        cart_item1 = ShoppingCart.objects.create(user=self.user, dish=self.dish1, quantity=2)
        cart_item2 = ShoppingCart.objects.create(user=self.user, dish=self.dish2, quantity=1)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Send a GET request to view the cart
        response = self.client.get('/api/cart/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_price'], 35.0)
        self.assertEqual(len(response.data['positions']), 2)

    def test_checkout(self):
        # Create cart items
        ShoppingCart.objects.create(user=self.user, dish=self.dish1, quantity=2)
        ShoppingCart.objects.create(user=self.user, dish=self.dish2, quantity=1)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Send a POST request to checkout the cart
        response = self.client.post('/api/cart/checkout/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the cart is empty after checkout
        self.assertEqual(ShoppingCart.objects.filter(user=self.user).count(), 0)

        # Check the creation of an order
        self.assertTrue(Order.objects.filter(user=self.user).exists())

    def test_order_list(self):
        # Create order records
        order1 = Order.objects.create(user=self.user, price=25.0, time=timezone.now())
        Position.objects.create(order=order1, dish=self.dish1, quantity=2)
        Position.objects.create(order=order1, dish=self.dish2, quantity=1)

        order2 = Order.objects.create(user=self.user, price=15.0, time=timezone.now())
        Position.objects.create(order=order2, dish=self.dish1, quantity=1)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Send a GET request to view the list of orders
        response = self.client.get('/api/orders/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_count'], 2)
        self.assertEqual(response.data['total_sum'], 40.0)
        self.assertEqual(len(response.data['last_orders']), 2)
        self.assertEqual(response.data['last_orders'][0]['id'], order2.id)
        self.assertEqual(response.data['last_orders'][1]['id'], order1.id)

    def tearDown(self):
        CustomUser.objects.all().delete()
        Restaurant.objects.all().delete()
        Dish.objects.all().delete()
        ShoppingCart.objects.all().delete()
        Order.objects.all().delete()
        Position.objects.all().delete()

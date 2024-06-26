from datetime import datetime
from api.models import Order, Position, Restaurant, Dish, ShoppingCart
from rest_framework import serializers


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price']


class RestaurantSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True)
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'dishes']


class AddToCartSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_dish_id(self, value):
        if not Dish.objects.filter(id=value).exists():
            raise serializers.ValidationError("Dish with this ID does not exist.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        dish_id = validated_data['dish_id']
        quantity = validated_data['quantity']
        dish = Dish.objects.get(id=dish_id)

        cart_item, created = ShoppingCart.objects.get_or_create(
            user=user,
            dish=dish,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item


class RemoveFromCartSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_dish_id(self, value):
        if not Dish.objects.filter(id=value).exists():
            raise serializers.ValidationError("Dish with this ID does not exist.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        dish_id = data['dish_id']
        if not ShoppingCart.objects.filter(user=user, dish_id=dish_id).exists():
            raise serializers.ValidationError("This dish is not in your cart.")
        return data

    def save(self):
        user = self.context['request'].user
        dish_id = self.validated_data['dish_id']
        quantity = self.validated_data['quantity']
        cart_item = ShoppingCart.objects.get(user=user, dish_id=dish_id)

        if cart_item.quantity > quantity:
            cart_item.quantity -= quantity
            cart_item.save()
        else:
            cart_item.delete()

        return cart_item


class PositionCartSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='dish.name')
    price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'quantity', 'price']

    def get_price(self, obj):
        return obj.dish.price * obj.quantity


class ShoppingCartSerializer(serializers.Serializer):
    total_price = serializers.SerializerMethodField()
    positions = PositionCartSerializer(many=True, source='shoppingcart_set')

    class Meta:
        fields = ['total_price', 'positions']

    def get_total_price(self, obj):
        return sum(item.dish.price * item.quantity for item in obj.shoppingcart_set.all())


class CheckoutSerializer(serializers.Serializer):
    def validate(self, data):
        user = self.context['request'].user
        cart_items = ShoppingCart.objects.filter(user=user)
        total_price = sum(item.dish.price * item.quantity for item in cart_items)

        if user.balance < total_price:
            raise serializers.ValidationError("Insufficient balance to complete the purchase.")

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")

        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        cart_items = ShoppingCart.objects.filter(user=user)
        total_price = sum(item.dish.price * item.quantity for item in cart_items)

        user.balance -= total_price
        user.save()

        order = Order.objects.create(user=user, price=total_price)

        for item in cart_items:
            Position.objects.create(
                order=order,
                dish=item.dish,
                quantity=item.quantity
            )

        cart_items.delete()

        return order
    
    
class PositionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='dish.name')
    price = serializers.FloatField(source='dish.price')

    class Meta:
        model = Position
        fields = ['id', 'name', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    positions = PositionSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'price', 'time', 'positions']

    def get_time(self, obj):
        return int(datetime.timestamp(obj.time))

class OrderListSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    total_sum = serializers.FloatField()
    last_orders = OrderSerializer(many=True)
from api.models import Order, Restaurant, ShoppingCart
from rest_framework import permissions, generics
from rest_framework.response import Response
from api.serializers import AddToCartSerializer, CheckoutSerializer, OrderListSerializer, RemoveFromCartSerializer, RestaurantSerializer, ShoppingCartSerializer
from rest_framework import status


class RestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        dish_name = self.request.query_params.get('name', None)
        restaurant_id = self.request.query_params.get('restaurant_id', None)

        if dish_name or restaurant_id:
            filtered_restaurants = []
            for restaurant in queryset:
                filtered_dishes = restaurant.dishes.all()
                if dish_name:
                    filtered_dishes = filtered_dishes.filter(name__icontains=dish_name)
                if restaurant_id:
                    filtered_dishes = filtered_dishes.filter(restaurant__id=restaurant_id)
                
                if filtered_dishes.exists():
                    filtered_restaurants.append(restaurant)

            return Restaurant.objects.filter(id__in=[r.id for r in filtered_restaurants])

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class AddToCartView(generics.GenericAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_item = serializer.save()
        return Response({
            "id": cart_item.id,
            "user": cart_item.user.id,
            "dish": cart_item.dish.id,
            "quantity": cart_item.quantity
        }, status=status.HTTP_200_OK)


class RemoveFromCartView(generics.GenericAPIView):
    serializer_class = RemoveFromCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_item = serializer.save()
        return Response({
            "id": cart_item.id if cart_item.pk else None,
            "user": request.user.id,
            "dish": cart_item.dish.id if cart_item.pk else None,
            "quantity": cart_item.quantity if cart_item.pk else 0
        }, status=status.HTTP_200_OK)


class ShoppingCartView(generics.GenericAPIView):
    serializer_class = ShoppingCartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        cart_items = ShoppingCart.objects.filter(user=user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class CheckoutView(generics.GenericAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Checkout successful"}, status=status.HTTP_200_OK)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(user=user).order_by('-time')[:10]

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_count = queryset.count()
        total_sum = sum(order.price for order in queryset)

        serializer = self.get_serializer({
            'total_count': total_count,
            'total_sum': total_sum,
            'last_orders': queryset
        })
        
        return Response(serializer.data)
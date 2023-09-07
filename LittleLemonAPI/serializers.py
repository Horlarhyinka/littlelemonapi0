from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["title", "id"]

class MenuItemsSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ["title", "price", "featured", "category_id", "category", "id"]

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemsSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Cart
        fields = ["user", "quantity", "unit_price", "price", "menuitem", "menuitem_id"]

class OrderSerializer(serializers.ModelSerializer):
    delivery_crew = serializers.IntegerField(required=False)
    class Meta:
        model = Order
        fields = ["user", "delivery_crew", "status"]

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemsSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = OrderItem
        fields = ["order", "menuitem", "quantity", "unit_price", "price", "order_id", "menuitem_id"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

from typing import Any
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .permissions import IsManager, IsDelivery, IsManagerOrDelivery
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseBadRequest
from django.contrib.auth.models import User, Group
from .serializers import CategorySerializer, MenuItemsSerializer, CartSerializer, OrderItemSerializer, OrderSerializer, UserSerializer
from .models import Category, MenuItem, Order, OrderItem, Cart
from django.core.paginator import Paginator

from .appgroups import GROUPS

# Create your views here.
class AssignManager(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"message": "username is required"})  
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name=GROUPS["MANAGER"])
        except User.DoesNotExist:
            return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        group.user_set.add(user)
        return Response({"message": f"{username} has been added to manager group"})
    def get(self, request):
        try:
            group = Group.objects.get(name=GROUPS["MANAGER"])
            users = User.objects.filter(groups=group)
        except User.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        serialized_user = UserSerializer(users, many=True)
        return Response(serialized_user.data, status=status.HTTP_200_OK)
    

class AssignDelivery(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"message": "username is required"})  
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name=GROUPS["DELIVERY"])
        except User.DoesNotExist:
            return Response({"message": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"message": "group not found"}, status=status.HTTP_404_NOT_FOUND)
        group.user_set.add(user)
        return Response({"message": f"{username} has been added to dlivery group"})
    def get(self, request):
        try:
            group = Group.objects.get(name=GROUPS["DELIVERY"])
            users = User.objects.filter(groups=group)
        except User.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        serialized_user = UserSerializer(users, many=True)
        return Response(serialized_user.data, status=status.HTTP_200_OK)


    

class CategoriesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsManager]
        self.check_permissions(request)
        title = request.data.get("title")
        data={"title": title}
        serialized_category = CategorySerializer(data=data)
        serialized_category.is_valid(raise_exception=True)
        cat = Category(title=title)
        cat.save()
        return Response(serialized_category.data, status=status.HTTP_201_CREATED)

class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    permission_classes = [IsManager]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer(Category)

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemsSerializer
    def list(self, request, *args, **kwargs):
        category = request.query_params.get("category")
        category_id = request.query_params.get("category_id")
        ordering = request.query_params.get("ordering")
        toprice = request.query_params.get("toprice")
        search = request.query_params.get("search")
        perpage = request.query_params.get("perpage")
        page = request.query_params.get("page")
        menuitems = MenuItem.objects.select_related("category")
        if category:
            menuitems = menuitems.filter(category__title=category)
        if category_id:
            menuitems = menuitems.filter(category__id = category_id)
        if toprice:
            menuitems = menuitems.filter(price__lte = toprice)
        if search:
            menuitems = menuitems.filter(title__icontains = search)
        if ordering:
            ordering_fields = ordering.split(",")
            menuitems = menuitems.filter(*ordering_fields)
        paginator = Paginator(menuitems, per_page=perpage or 5)
        if page:
            menuitems = paginator.page(page)
        else:
            menuitems = paginator.page(1)
        serialized_menuitems = MenuItemsSerializer(menuitems, many=True)
        return Response(serialized_menuitems.data, status=status.HTTP_200_OK)
    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsManager]
        self.check_permissions(request)
        category_id = request.data.get("category_id")
        price = request.data.get("price")
        featured = request.data.get("featured")
        title = request.data.get("title")
        menuitem = MenuItem(category_id=category_id, price=price, featured=featured, title=title)
        serialized = MenuItemsSerializer(data={"title": title, "price": price, "category_id": category_id, "featured": featured})
        serialized.is_valid(raise_exception=True)
        serialized.save()
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field="id"
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    permission_classes = [IsManager]


class CartViews(APIView):
    # permission_classes = [IsAuthenticated]
    # queryset = Cart.objects.all()
    def get(self, req):
        user = req.user
        try:
            cart = Cart.objects.get(user=user.pk)
        except Cart.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        serialized_cart = CartSerializer(cart)
        return Response(serialized_cart.data, status=status.HTTP_200_OK)
    def post(self, req):
        user = req.user
        menuitem_id = req.data.get("menuitem_id")
        quantity = req.data.get("quantity")
        if not menuitem_id:
            return Response({"message": "field menuitem_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not quantity:
            return Response({"message": "field quantity is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = MenuItem.objects.get(id=menuitem_id) 
        except MenuItem.DoesNotExist:
            return Response({"message": "menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            existing = Cart.objects.get(user=user.pk)
        except Cart.DoesNotExist:
            data={"menuitem_id": menuitem_id, "user": user.pk, "quantity": quantity, "price": item.price,"unit_price": item.price}
            serialized = CartSerializer(data=data)
            serialized.is_valid(raise_exception=True) 
            serialized.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        return Response({"message": "duplicate cart is not allowed"}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, req):
        try:
            cart = Cart.objects.get(user=req.user.pk)
        except Cart.DoesNotExist:
            return Response({"message": "cart not found"}, status=status.HTTP_404_NOT_FOUND)
        res = cart.delete()
        return Response({"message": "cart items deleted"}, status=status.HTTP_204_NO_CONTENT)

class SingleCartView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    lookup_field="id"


class OrdersView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    permission_classes = []

class OrderItemsView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    def post(self, request):
        usercart = Cart.objects.get(user= request.user.pk)
        menuitem = usercart.menuitem
        if not menuitem:
            return Response({"message": "menu item does not exist"})
        #create order
        serialized = OrderSerializer(data={"user": request.user.pk, "status": 0})
        serialized.is_valid(raise_exception=True)
        serialized = serialized.save()
        order = serialized
        #createorderitem
        serializedorderitem = OrderItemSerializer(data={"order_id": order.id, "menuitem_id": menuitem.id, "price": usercart.price, "unit_price": usercart.unit_price, "quantity":usercart.quantity})
        serializedorderitem.is_valid(raise_exception=True)
        serializedorderitem.save()
        #remove order from cart
        usercart.delete()
        return Response(serializedorderitem.data, status=status.HTTP_201_CREATED)
    
class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderItem.objects.all()
    lookup_field = "id"
    
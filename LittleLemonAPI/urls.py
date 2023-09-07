from django.urls import path
from . import views

urlpatterns = [
    path("roles/manager/users", views.AssignManager.as_view(), name="assign_manager"),
    path("roles/delivery/users", views.AssignDelivery.as_view(), name="assign_delivery"),
    path("categories", views.CategoriesView.as_view(), name="categories"),
    path("categories/<int:id>", views.SingleCategoryView.as_view(), name="categories"),
    path("menu-items", views.MenuItemsView.as_view(), name="menu_items"),
    path("menu-items/<int:id>", views.SingleMenuItemView.as_view(), name="menu_items"),
    path("cart/menu-items", views.CartViews.as_view(), name="cart"),
    path("carts/menu-items/<int:id>", views.SingleCartView.as_view(), name="cart"),
    path("orders", views.OrderItemsView.as_view(), name="orders"),
    path("order/<int:id>", views.SingleOrderView.as_view(), name="order")
]
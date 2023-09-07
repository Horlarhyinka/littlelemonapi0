from rest_framework.permissions import BasePermission
from .appgroups import GROUPS

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name=GROUPS["MANAGER"]).exists()
    
class IsDelivery(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name=GROUPS["DELIVERY"]).exists()
    
class IsManagerOrDelivery(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.groups.filter(name=GROUPS["MANAGER"]).exists() or request.user.groups.filter(name=GROUPS["DELIVERY"]).exists())
      
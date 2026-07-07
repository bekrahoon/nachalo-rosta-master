"""
Custom permissions for the accounts app and other apps.
"""

from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwner(permissions.BasePermission):
    """
    Allow access only to the object owner.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or obj == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow access only to the object owner.
    Read permission allowed to any access.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user or obj == request.user


class IsOrganizer(permissions.BasePermission):
    """
    Allow access only to users with organizer role.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['organizer', 'admin']


class IsOrganizerOrAdmin(permissions.BasePermission):
    """
    Allow access only to organizers and admins.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_organizer


class IsAdmin(permissions.BasePermission):
    """
    Allow access only to admins.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsModerator(permissions.BasePermission):
    """
    Allow access only to moderators and admins.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_moderator


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access to owner of object or admin.
    """
    
    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user or
            request.user.is_authenticated and request.user.role == 'admin'
        )


class IsVerifiedEmail(permissions.BasePermission):
    """
    Allow access only to users with verified email.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.email_verified
        )


class IsActive(permissions.BasePermission):
    """
    Allow access only to active users.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class CanEditUser(permissions.BasePermission):
    """
    Allow user to edit own profile or admin to edit any user.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True
        if request.user.role == 'admin':
            return True
        return False


class IsEmailVerified(permissions.BasePermission):
    """
    Check if user's email is verified.
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.email_verified
        return False


class CanCreateEvent(permissions.BasePermission):
    """
    Only organizers and admins can create events.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_organizer or request.user.role == 'admin'


class CanModerateContent(permissions.BasePermission):
    """
    Only moderators and admins can moderate content.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_moderator or request.user.role == 'admin'

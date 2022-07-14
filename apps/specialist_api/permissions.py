from rest_framework.permissions import BasePermission

from django.shortcuts import get_object_or_404

from .models import Worker


class IsWorkerOrAdmin(BasePermission):
    """
    Provides permission for the user if he is a worker or an admin. 
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        worker = get_object_or_404(Worker, id=view.kwargs['worker_id'])
        if worker.profile == request.user:
            return True

        return False

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


ROLE_CHOICES = (
    (0, 'common_user'),
    (1, 'admin')
)


class CustomUser(AbstractUser):
    """
    Stores a single user entry.
    """
    role = models.IntegerField(default=0, choices=ROLE_CHOICES)
    
    REQUIRED_FIELDS = [
        'email',
        'password',
    ]
    objects = UserManager()
    
    class Meta:
        db_table = 'custom_user'
    
    def __str__(self):
        return self.username

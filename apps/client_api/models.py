from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from appointments_project import settings


User = get_user_model()


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    
    class Meta:
        db_table = 'client'
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

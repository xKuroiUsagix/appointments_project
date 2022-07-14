from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('Username not given.')
        if not email:
            raise ValueError('Email not given.')
        
        email = self.normalize_email(email)
        if extra_fields.get('confirm_password') is not None:
            extra_fields.pop('confirm_password')
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 1)
        
        if extra_fields.get('role') != 1:
            raise ValueError('Superuser role must be equals to 1')
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser 'is_superuser' must be True")
        return self.create_user(username, email, password, **extra_fields)

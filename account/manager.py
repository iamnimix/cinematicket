from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create(self, phone, password, **kwargs):
        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)
        return self.create(phone=phone, password=password, **kwargs)
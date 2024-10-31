
# from comtypes.automation import _
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    # create user with given number and password
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('شماره تلفن باید وارد شود')

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError(_('Superuser must have is_staff=True.'))
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(phone, password, **extra_fields)

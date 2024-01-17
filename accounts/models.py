from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('Email is mandatory')
        if not username:
            raise ValueError('User Name is mandatory')
    
        user = self.model(
            # this will convert any capitals in email to small
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        # setting the password with the inbuilt function set_password
        user.set_password(password)

        # saving the user to database
        user.save(using = self._db)

        # returning user object
        return user
    
    def create_superuser(self, first_name, last_name, username, email, password):
        # creating super user with the help of create_user method
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )

        # giving all the permissions to the super user
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True

        # saving the super user with all the permissions
        user.save(using = self._db)

        # returning superuser
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    username = models.CharField(max_length = 50, unique = True)
    email = models.EmailField(max_length = 100, unique = True)
    phone_number = models.CharField(max_length = 10)

    # Required fields
    date_joined = models.DateTimeField(auto_now = True)
    last_login = models.DateTimeField(auto_now_add = True)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(default = False)
    is_superadmin = models.BooleanField(default = False)

    # instead of username we are taking email as login credential
    USERNAME_FIELD = 'email'
    
    # the below fields are required while creating an account
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    # specifying that we are using the MyAccountManager for all the operations 
    objects = MyAccountManager()

    # in the django pannel we want to show emails instead of account object
    def __str__(self):
        return self.email
    
    # checking if it is admin then has all the permissions
    def has_perm(self, perm, obj = None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True